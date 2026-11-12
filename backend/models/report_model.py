import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

from backend.extractors.domus_api import extrair_p1_domus, formatar_p1_domus
from backend.extractors.anel_playwright import extrair_anel_comutado, formatar_anel_comutado
from backend.extractors.enm_cli import (
    extrair_celldowntime_enm,
    formatar_celldowntime,
    processar_texto_cli_enm,
    carregar_dicionario_sites_enm,
    disparar_worker_enm_segundo_plano,
    obter_status_job_enm,
    COMANDOS_ENM_CLI,
    ENM_URL_PADRAO,
)


# Nomes de abas no Excel estritamente padronizados conforme solicitado:
# portal_calamidade => P1
# export => AnelComutado
# Consolidado_CellDowntime => CellDowntime
CATALOGO_RELATORIOS = {
    "p1_domus": {
        "id": "p1_domus",
        "nome": "P1 (DOMUS)",
        "aba_excel": "P1",
        "origem": "API DOMUS (10.215.39.118:8001)",
        "extrator": extrair_p1_domus,
        "formatador": formatar_p1_domus,
        "colunas_filtro_sugeridas": ["uf", "ddd", "municipio", "grupo_responsavel", "técnico", "status atualizado"],
        "colunas_editaveis": ["técnico", "data", "status atualizado"],
    },
    "anel_comutado": {
        "id": "anel_comutado",
        "nome": "Anel Comutado (BI)",
        "aba_excel": "AnelComutado",
        "origem": "Portal BI (Playwright)",
        "extrator": extrair_anel_comutado,
        "formatador": formatar_anel_comutado,
        "colunas_filtro_sugeridas": [
            "UF",
            "Prioridade",
            "Aging",
            "Classificação",
            "GRUPO_PLANTA_INTERNA",
            "Gestor Atual",
            "Localidade",
        ],
        "colunas_editaveis": ["Técnico", "Data", "Observação"],
    },
    "celldowntime": {
        "id": "celldowntime",
        "nome": "CellDowntime (ENM CLI)",
        "aba_excel": "CellDowntime",
        "origem": "Ericsson ENM CLI (2º Plano Automático)",
        "extrator": extrair_celldowntime_enm,
        "formatador": formatar_celldowntime,
        "colunas_filtro_sugeridas": ["Fonte", "UF", "Localidade", "Campo", "Reincidente", "Pend. Noc"],
        "colunas_editaveis": ["TA", "Campo", "Observação", "Reincidente", "Técnico", "Previsão", "Pend. Noc"],
    },
}


class ReportModel:
    """
    Model MVC que gerencia os 3 relatórios e mantém o Worker do Ericsson ENM CLI
    executando automaticamente em segundo plano.
    """

    def __init__(self):
        self.estado_memoria: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def obter_modo_ambiente() -> str:
        return os.getenv("ENV_MODE", "MOCK").upper()

    def inicializar_todos(self):
        self.carregar_relatorio("p1_domus")
        self.carregar_relatorio("anel_comutado")
        # Carrega estado inicial e também dispara o worker assíncrono em 2º plano para o ENM CLI
        self.carregar_relatorio("celldowntime")
        self.iniciar_enm_em_segundo_plano()

    def iniciar_enm_em_segundo_plano(self):
        modo = self.obter_modo_ambiente()

        def _ao_concluir_enm(df_enm: pd.DataFrame):
            agora = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (Job ENM 2º Plano)"
            self.estado_memoria["celldowntime"] = {
                "df": df_enm.reset_index(drop=True),
                "atualizado_em": agora,
                "erro": None,
            }

        disparar_worker_enm_segundo_plano(modo, on_complete=_ao_concluir_enm)

    def _descobrir_colunas_filtraveis(self, df: pd.DataFrame, sugeridas: List[str]) -> Dict[str, List[str]]:
        if df is None or df.empty:
            return {}
        opcoes = {}
        ordenadas = [c for c in sugeridas if c in df.columns] + [
            c for c in df.columns if c not in sugeridas
        ]
        for col in ordenadas:
            valores = [v for v in df[col].dropna().astype(str).unique().tolist() if v.strip() != ""]
            if 1 <= len(valores) <= 60 and col.lower() not in ("alarme", "sequencia", "ticket"):
                opcoes[col] = sorted(valores)
                if len(opcoes) >= 6:
                    break
        return opcoes

    def carregar_relatorio(self, report_id: str) -> Dict[str, Any]:
        if report_id not in CATALOGO_RELATORIOS:
            raise ValueError(f"Relatório '{report_id}' não existe.")

        meta = CATALOGO_RELATORIOS[report_id]
        modo = self.obter_modo_ambiente()

        try:
            df = meta["extrator"](modo)
            erro_msg = None
        except Exception as exc:
            df = pd.DataFrame()
            erro_msg = str(exc)

        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.estado_memoria[report_id] = {
            "df": df.reset_index(drop=True),
            "atualizado_em": agora,
            "erro": erro_msg,
        }
        return self.serializar_relatorio(report_id)

    def importar_dataframe(self, report_id: str, df_bruto: pd.DataFrame, origem_label: str) -> Dict[str, Any]:
        if report_id not in CATALOGO_RELATORIOS:
            raise ValueError(f"Relatório '{report_id}' inválido.")

        meta = CATALOGO_RELATORIOS[report_id]
        df_formatado = meta["formatador"](df_bruto)
        agora = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ({origem_label})"
        self.estado_memoria[report_id] = {
            "df": df_formatado.reset_index(drop=True),
            "atualizado_em": agora,
            "erro": None,
        }
        return self.serializar_relatorio(report_id)

    def importar_cli_enm_colado(self, fonte: str, texto_cli: str) -> Dict[str, Any]:
        if fonte not in ("P1", "4G_5G", "3G"):
            raise ValueError("Fonte ENM deve ser 'P1', '4G_5G' ou '3G'.")

        mapa_sites = carregar_dicionario_sites_enm()
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        novas_linhas = processar_texto_cli_enm(texto_cli, fonte, mapa_sites, hoje_str)
        if not novas_linhas:
            raise ValueError("Nenhuma linha válida de alarme ENM identificada no texto colado.")

        df_novo = pd.DataFrame(novas_linhas)
        estado_atual = self.estado_memoria.get("celldowntime")
        if estado_atual and not estado_atual["df"].empty:
            df_existente = estado_atual["df"]
            df_outras = df_existente[df_existente["Fonte"] != fonte]
            df_combinado = pd.concat([df_outras, df_novo], ignore_index=True)
        else:
            df_combinado = df_novo

        self.estado_memoria["celldowntime"] = {
            "df": df_combinado.reset_index(drop=True),
            "atualizado_em": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (CLI ENM: {fonte})",
            "erro": None,
        }
        return self.serializar_relatorio("celldowntime")

    def atualizar_celula(self, report_id: str, row_idx: int, coluna: str, valor: str) -> bool:
        if report_id not in self.estado_memoria:
            return False
        df: pd.DataFrame = self.estado_memoria[report_id]["df"]
        if 0 <= row_idx < len(df) and coluna in df.columns:
            df.at[row_idx, coluna] = str(valor or "").strip()
            return True
        return False

    def serializar_relatorio(self, report_id: str) -> Dict[str, Any]:
        meta = CATALOGO_RELATORIOS[report_id]
        estado = self.estado_memoria.get(report_id)
        if not estado:
            return self.carregar_relatorio(report_id)

        df: pd.DataFrame = estado["df"]
        registros = []
        if not df.empty:
            for idx, row in df.fillna("").iterrows():
                item = row.to_dict()
                item["_row_idx"] = int(idx)
                registros.append(item)

        colunas = list(df.columns) if not df.empty else []
        filtros_disponiveis = self._descobrir_colunas_filtraveis(df, meta["colunas_filtro_sugeridas"])

        payload = {
            "id": report_id,
            "nome": meta["nome"],
            "aba_excel": meta["aba_excel"],
            "origem": meta["origem"],
            "atualizado_em": estado["atualizado_em"],
            "erro": estado["erro"],
            "colunas": colunas,
            "colunas_editaveis": meta["colunas_editaveis"],
            "registros": registros,
            "filtros_disponiveis": filtros_disponiveis,
        }
        if report_id == "celldowntime":
            payload["enm_cli_info"] = {
                "url": ENM_URL_PADRAO,
                "comandos": COMANDOS_ENM_CLI,
                "status_background": obter_status_job_enm(),
            }
        return payload

    @staticmethod
    def aplicar_filtros_dataframe(
        df: pd.DataFrame, filtros: Dict[str, str], termo_busca: str
    ) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame() if df is None else df

        df_out = df.copy()
        for col, valor in (filtros or {}).items():
            if valor and valor != "TODOS" and col in df_out.columns:
                df_out = df_out[df_out[col].astype(str) == str(valor)]

        if termo_busca and termo_busca.strip():
            termo = termo_busca.strip().lower()
            mascara = df_out.astype(str).apply(
                lambda row: any(termo in str(v).lower() for v in row), axis=1
            )
            df_out = df_out[mascara]

        return df_out
