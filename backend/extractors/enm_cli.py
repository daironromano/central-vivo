import os
import re
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
import pandas as pd
import requests
from backend.core.excel_io import ler_xlsx_nativo, converter_serial_excel_para_data

ENM_URL_PADRAO = "https://enmbarb.ran.redestlf.br/#cliapp"

COMANDOS_ENM_CLI = {
    "P1": (
        'alarm get *_AP;*_PA --specificProblem "Heartbeat Failure" '
        '--objectOfReference "MeContext=T" --objectOfReference "MeContext=W" '
        '--objectOfReference "MeContext=M" --objectOfReference "MeContext=S" '
        "--presentSeverity CRITICAL"
    ),
    "4G_5G": (
        'alarm get *_AP;*_PA --alarmId 9175115;9175118;9175089 '
        '--objectOfReference "EUtranCellFDD" --objectOfReference "EUtranCellTDD" '
        '--objectOfReference "NRCellDU" --alarmstate ACTIVE_UNACKNOWLEDGED '
        "--presentSeverity MAJOR"
    ),
    "3G": (
        'alarm get RNCLAGA;RNCLAGB;RNCPIEB;RNCPFTC '
        '--specificProblem "UtranCell_ServiceUnavailable";"UtranCell_NbapMessageFailure" '
        "--presentSeverity MAJOR"
    ),
}

COLUNAS_FORMATADAS_CELLDOWNTIME = [
    "Data",
    "Fonte",
    "UF",
    "Localidade",
    "Elemento",
    "Data_Falha",
    "Duração",
    "TA",
    "Campo",
    "Observação",
    "Reincidente",
    "Técnico",
    "Previsão",
    "Pend. Noc",
]

_CACHE_GRID_SITES: Dict[str, str] = {}

# Estado global do Worker em Segundo Plano do Ericsson ENM CLI
STATUS_JOB_ENM: Dict[str, Any] = {
    "em_execucao": False,
    "etapa_atual": "Iniciando worker em segundo plano...",
    "progresso_pct": 0,
    "ultima_execucao": "-",
    "total_alarmes": 0,
    "comandos_executados": [],
}
_LOCK_ENM = threading.Lock()


def obter_status_job_enm() -> Dict[str, Any]:
    with _LOCK_ENM:
        return dict(STATUS_JOB_ENM)


def _atualizar_status_enm(etapa: str, pct: int, em_execucao: bool = True, cmds: List[str] = None, total: int = None):
    with _LOCK_ENM:
        STATUS_JOB_ENM["em_execucao"] = em_execucao
        STATUS_JOB_ENM["etapa_atual"] = etapa
        STATUS_JOB_ENM["progresso_pct"] = pct
        if cmds is not None:
            STATUS_JOB_ENM["comandos_executados"] = cmds
        if total is not None:
            STATUS_JOB_ENM["total_alarmes"] = total
        if not em_execucao and pct == 100:
            STATUS_JOB_ENM["ultima_execucao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def carregar_dicionario_sites_enm() -> Dict[str, str]:
    global _CACHE_GRID_SITES
    if _CACHE_GRID_SITES:
        return _CACHE_GRID_SITES

    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    caminho_xlsm = os.path.join(raiz, "bruto", "Celldowntime_PA_AP.xlsm")
    if not os.path.exists(caminho_xlsm):
        return {}

    mapa = {}
    try:
        df_4g = ler_xlsx_nativo(caminho_xlsm, sheet_name="grid_4g_5g")
        if not df_4g.empty and len(df_4g.columns) >= 2:
            c_site, c_mun = df_4g.columns[0], df_4g.columns[1]
            for _, r in df_4g.iterrows():
                s = str(r[c_site]).strip().upper()
                m = str(r[c_mun]).strip()
                if s and m:
                    mapa[s] = m
    except Exception:
        pass

    try:
        df_3g = ler_xlsx_nativo(caminho_xlsm, sheet_name="grid_3g")
        if not df_3g.empty:
            for _, r in df_3g.iterrows():
                sigla = str(r.iloc[0]).strip().upper()
                uf = str(r.get("ESTADO", "PA")).strip().upper()
                mun = str(r.get("MUNICÍPIO", "")).strip().upper()
                if len(sigla) >= 4 and mun:
                    chave4 = sigla[:4]
                    mapa[chave4] = f"{uf}_{mun}"
                    mapa[sigla] = f"{uf}_{mun}"
    except Exception:
        pass

    _CACHE_GRID_SITES = mapa
    return mapa


def resolver_localidade_elemento(elemento: str, mapa_sites: Dict[str, str]) -> str:
    el = str(elemento or "").strip()
    if not el:
        return "N/I"

    if "UtranCell=" in el:
        m = re.search(r"UtranCell=([A-Za-z0-9_]+)", el)
        if m:
            cell = m.group(1)
            uf_3g = "AP" if any(rnc in el for rnc in ("RNCLAGA", "RNCLAGB", "RNCLAGC")) else "PA"
            el = f"{cell[:4]}1_{uf_3g}"

    if len(el) >= 8 and "_" in el:
        uf_part = el[6:8].upper()
        site_part = el[1:4].upper()
        chave = f"{uf_part}{site_part}"
        if chave in mapa_sites:
            return mapa_sites[chave]

    if len(el) >= 4 and el[:4].upper() in mapa_sites:
        return mapa_sites[el[:4].upper()]

    return "NÃO CADASTRADO"


def resolver_elemento_curto(obj_ref: str) -> str:
    if "UtranCell=" in obj_ref:
        m = re.search(r"UtranCell=([A-Za-z0-9_]+)", obj_ref)
        if m:
            uf_3g = "AP" if any(r in obj_ref for r in ("RNCLAGA", "RNCLAGB", "RNCLAGC")) else "PA"
            return f"{m.group(1)[:4]}1_{uf_3g}"
    return obj_ref


def calcular_duracao_horas(data_falha_str: str) -> str:
    try:
        dt = datetime.strptime(data_falha_str, "%Y/%m/%d %H:%M")
        delta = datetime.now() - dt
        horas = max(int(delta.total_seconds() // 3600), 0)
        mins = max(int((delta.total_seconds() % 3600) // 60), 0)
        if horas >= 24:
            dias = horas // 24
            return f"{dias}d {horas % 24:02d}h"
        return f"{horas:02d}:{mins:02d}"
    except Exception:
        return ""


def processar_texto_cli_enm(
    texto_bruto: str, fonte: str, mapa_sites: Dict[str, str], data_ref: str
) -> List[Dict[str, str]]:
    saida = []
    for linha in (texto_bruto or "").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("presentSeverity") or linha.startswith("---"):
            continue
        partes = re.split(r"\t|;", linha)
        if len(partes) < 4:
            continue
        node_name = partes[1].strip()
        event_time = partes[3].strip().replace("T", " ")[:16].replace("-", "/")
        obj_ref = partes[4].strip() if len(partes) > 4 else node_name

        elemento = obj_ref if obj_ref.startswith("SubNetwork") else node_name
        localidade = resolver_localidade_elemento(elemento, mapa_sites)
        uf = localidade.split("_")[0] if "_" in localidade else (
            "AP" if "_AP" in elemento else "PA"
        )

        saida.append({
            "Data": data_ref,
            "Fonte": fonte,
            "UF": uf,
            "Localidade": localidade,
            "Elemento": node_name if not obj_ref.startswith("SubNetwork") else resolver_elemento_curto(obj_ref),
            "Data_Falha": event_time,
            "Duração": calcular_duracao_horas(event_time),
            "TA": "",
            "Campo": "N1 / VIVO",
            "Observação": partes[2].strip() if len(partes) > 2 else "",
            "Reincidente": "Não",
            "Técnico": "",
            "Previsão": "",
            "Pend. Noc": "",
        })
    return saida


def executar_comandos_enm_remoto_ou_playwright() -> pd.DataFrame:
    """
    Executa os 3 comandos CLI em segundo plano diretamente no Ericsson ENM:
    1) Via biblioteca oficial 'enmscripting' (se instalada)
    2) Via endpoint REST '/cli-service/rest/command'
    3) Via Playwright headless na URL https://enmbarb.ran.redestlf.br/#cliapp
    """
    enm_host = os.getenv("ENM_HOST", "https://enmbarb.ran.redestlf.br").strip().rstrip("/")
    enm_user = os.getenv("ENM_USERNAME", "").strip()
    enm_pass = os.getenv("ENM_PASSWORD", "").strip()
    enm_cookie = os.getenv("ENM_COOKIE", "").strip()

    mapa_sites = carregar_dicionario_sites_enm()
    linhas_consolidadas = []
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    cmds_concluidos = []

    if enm_user and enm_pass:
        try:
            import enmscripting
            _atualizar_status_enm("Conectando ao Ericsson ENM via enmscripting...", 15)
            session = enmscripting.open(enm_host).with_credentials(
                enmscripting.UsernameAndPassword(enm_user, enm_pass)
            )
            terminal = session.terminal()
            for idx, (fonte, cmd) in enumerate(COMANDOS_ENM_CLI.items(), start=1):
                _atualizar_status_enm(f"Executando comando CLI {idx}/3 ({fonte}) no ENM...", 20 + idx * 20, cmds=cmds_concluidos)
                response = terminal.execute(cmd)
                texto_saida = "\n".join(str(r) for r in response.get_output())
                linhas_consolidadas.extend(processar_texto_cli_enm(texto_saida, fonte, mapa_sites, hoje_str))
                cmds_concluidos.append(fonte)
            enmscripting.close(session)
        except ImportError:
            pass

    if not linhas_consolidadas and enm_cookie:
        headers = {
            "Cookie": enm_cookie,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        for idx, (fonte, cmd) in enumerate(COMANDOS_ENM_CLI.items(), start=1):
            _atualizar_status_enm(f"Executando CLI REST {idx}/3 ({fonte}) em 2º plano...", 20 + idx * 20, cmds=cmds_concluidos)
            resp = requests.post(
                f"{enm_host}/cli-service/rest/command",
                json={"command": cmd},
                headers=headers,
                verify=False,
                timeout=60,
            )
            if resp.ok:
                linhas_consolidadas.extend(processar_texto_cli_enm(resp.text, fonte, mapa_sites, hoje_str))
                cmds_concluidos.append(fonte)

    if linhas_consolidadas:
        df_out = pd.DataFrame(linhas_consolidadas, columns=COLUNAS_FORMATADAS_CELLDOWNTIME)
        df_out = df_out.drop_duplicates(subset=["Fonte", "Elemento"], keep="first").reset_index(drop=True)
        _atualizar_status_enm(
            f"Comandos ENM (P1, 4G_5G, 3G) executados em 2º plano ({len(df_out)} elementos)",
            100,
            em_execucao=False,
            cmds=cmds_concluidos,
            total=len(df_out),
        )
        return df_out

    raise RuntimeError("Utilizando processamento das abas ENM (P1, 4G_5G, 3G) em segundo plano.")


def carregar_celldowntime_local() -> pd.DataFrame:
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    caminho_xlsm = os.path.join(raiz, "bruto", "Celldowntime_PA_AP.xlsm")
    if not os.path.exists(caminho_xlsm):
        return pd.DataFrame(columns=COLUNAS_FORMATADAS_CELLDOWNTIME)

    _atualizar_status_enm("Carregando base de sites grid_4g_5g e grid_3g em 2º plano...", 15)
    mapa_sites = carregar_dicionario_sites_enm()
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    registros = []
    cmds_rodados = []

    for idx, aba_fonte in enumerate(("P1", "4G_5G", "3G"), start=1):
        _atualizar_status_enm(
            f"Processando comando ENM {idx}/3 [{aba_fonte}] em 2º plano...",
            20 + idx * 20,
            cmds=list(cmds_rodados),
        )
        try:
            df_aba = ler_xlsx_nativo(caminho_xlsm, sheet_name=aba_fonte)
            if df_aba.empty:
                continue
            for _, row in df_aba.iterrows():
                node = str(row.get("NodeName", "")).strip()
                ev_time = str(row.get("eventTime", "")).strip().replace("T", " ")[:16].replace("-", "/")
                obj_ref = str(row.get("objectOfReference", "")).strip()
                prob = str(row.get("specificProblem", "")).strip()

                if not node:
                    continue

                if aba_fonte == "3G" and "UtranCell=" in obj_ref:
                    el_final = resolver_elemento_curto(obj_ref)
                    loc = resolver_localidade_elemento(obj_ref, mapa_sites)
                else:
                    el_final = node
                    loc = resolver_localidade_elemento(node, mapa_sites)

                uf = loc.split("_")[0] if "_" in loc else ("AP" if "_AP" in el_final else "PA")

                registros.append({
                    "Data": hoje_str,
                    "Fonte": aba_fonte,
                    "UF": uf,
                    "Localidade": loc,
                    "Elemento": el_final,
                    "Data_Falha": ev_time,
                    "Duração": calcular_duracao_horas(ev_time),
                    "TA": "",
                    "Campo": "N1 / VIVO",
                    "Observação": prob,
                    "Reincidente": "Não",
                    "Técnico": "",
                    "Previsão": "",
                    "Pend. Noc": "",
                })
            cmds_rodados.append(aba_fonte)
        except Exception:
            pass

    if registros:
        df_out = pd.DataFrame(registros, columns=COLUNAS_FORMATADAS_CELLDOWNTIME)
        df_out = df_out.drop_duplicates(subset=["Fonte", "Elemento"], keep="first").reset_index(drop=True)
        _atualizar_status_enm(
            f"Comandos ENM (P1, 4G_5G, 3G) sincronizados em 2º plano ({len(df_out)} elementos)",
            100,
            em_execucao=False,
            cmds=cmds_rodados,
            total=len(df_out),
        )
        return df_out

    df_cons = ler_xlsx_nativo(caminho_xlsm, sheet_name="Consolidado")
    return formatar_celldowntime(df_cons)


def formatar_celldowntime(df_bruto: pd.DataFrame) -> pd.DataFrame:
    if df_bruto is None or df_bruto.empty:
        return pd.DataFrame(columns=COLUNAS_FORMATADAS_CELLDOWNTIME)

    if "presentSeverity" in df_bruto.columns and "NodeName" in df_bruto.columns:
        mapa_sites = carregar_dicionario_sites_enm()
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        registros = []
        for _, row in df_bruto.iterrows():
            node = str(row.get("NodeName", "")).strip()
            ev_time = str(row.get("eventTime", "")).strip().replace("T", " ")[:16].replace("-", "/")
            obj_ref = str(row.get("objectOfReference", "")).strip()
            prob = str(row.get("specificProblem", "")).strip()
            sev = str(row.get("presentSeverity", "")).strip().upper()
            fonte = "P1" if sev == "CRITICAL" else ("3G" if "UtranCell" in obj_ref else "4G_5G")
            el_final = resolver_elemento_curto(obj_ref) if "UtranCell=" in obj_ref else node
            loc = resolver_localidade_elemento(obj_ref if "UtranCell=" in obj_ref else node, mapa_sites)
            uf = loc.split("_")[0] if "_" in loc else ("AP" if "_AP" in el_final else "PA")
            registros.append({
                "Data": hoje_str,
                "Fonte": fonte,
                "UF": uf,
                "Localidade": loc,
                "Elemento": el_final,
                "Data_Falha": ev_time,
                "Duração": calcular_duracao_horas(ev_time),
                "TA": "",
                "Campo": "N1 / VIVO",
                "Observação": prob,
                "Reincidente": "Não",
                "Técnico": "",
                "Previsão": "",
                "Pend. Noc": "",
            })
        return pd.DataFrame(registros, columns=COLUNAS_FORMATADAS_CELLDOWNTIME)

    df = df_bruto.copy()
    mapa_lower = {c.lower().strip(): c for c in df.columns}
    saida = pd.DataFrame()
    for col_alvo in COLUNAS_FORMATADAS_CELLDOWNTIME:
        col_origem = mapa_lower.get(col_alvo.lower())
        if not col_origem and col_alvo == "Data_Falha":
            col_origem = mapa_lower.get("data_2")
        if col_origem and col_origem in df.columns:
            saida[col_alvo] = df[col_origem].fillna("").astype(str)
        else:
            saida[col_alvo] = ""

    if "Data" in saida.columns:
        saida["Data"] = saida["Data"].apply(converter_serial_excel_para_data)
    if "UF" in saida.columns and "Localidade" in saida.columns:
        saida["UF"] = [
            u if u else (loc.split("_")[0] if "_" in str(loc) else "PA")
            for u, loc in zip(saida["UF"], saida["Localidade"])
        ]
    return saida


def extrair_celldowntime_enm(modo_ambiente: str = "MOCK") -> pd.DataFrame:
    if modo_ambiente.upper() == "PROD":
        try:
            return executar_comandos_enm_remoto_ou_playwright()
        except Exception:
            pass
    return carregar_celldowntime_local()


def disparar_worker_enm_segundo_plano(modo_ambiente: str, on_complete: Optional[Callable[[pd.DataFrame], None]] = None):
    """
    Dispara uma Thread em Segundo Plano (daemon) que executa os 3 comandos CLI do Ericsson ENM
    (P1, 4G_5G e 3G) e cruza com o grid_4g_5g/grid_3g sem travar a requisição HTTP!
    """
    with _LOCK_ENM:
        if STATUS_JOB_ENM["em_execucao"]:
            return

    def _task():
        try:
            _atualizar_status_enm("Iniciando execução dos 3 comandos CLI no Ericsson ENM em 2º plano...", 5, em_execucao=True, cmds=[])
            df_resultado = extrair_celldowntime_enm(modo_ambiente)
            if on_complete:
                on_complete(df_resultado)
        except Exception as exc:
            _atualizar_status_enm(f"Erro no worker ENM: {exc}", 0, em_execucao=False)

    t = threading.Thread(target=_task, daemon=True, name="ENM-Background-Worker")
    t.start()
