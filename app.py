import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file

from src.extractors.domus_api import extrair_p1_domus
from src.extractors.anel_bi import extrair_anel_comutado
from src.extractors.maestro_backlog import extrair_backlog_maestro
from src.core.excel_builder import gerar_excel_unificado
from src.core.excel_io import ler_xlsx_nativo

load_dotenv()

app = Flask(__name__)

# Definição dos 3 relatórios do sistema
CATALOGO_RELATORIOS = {
    "p1_domus": {
        "id": "p1_domus",
        "nome": "P1",
        "aba_excel": "P1_DOMUS",
        "origem": "",
        "extrator": extrair_p1_domus,
        "colunas_filtro_sugeridas": ["Regional", "UF", "Status", "SLA_Status", "Causa_Raiz", "Responsavel"],
    },
    "anel_comutado": {
        "id": "anel_comutado",
        "nome": "Anel Comutado",
        "aba_excel": "Anel_Comutado",
        "origem": "",
        "extrator": extrair_anel_comutado,
        "colunas_filtro_sugeridas": ["Regional", "UF", "Status_Anel", "Severidade", "Tecnologia"],
    },
    "backlog_maestro": {
        "id": "backlog_maestro",
        "nome": "Backlog Diário",
        "aba_excel": "Backlog_Maestro",
        "origem": "",
        "extrator": extrair_backlog_maestro,
        "colunas_filtro_sugeridas": ["Regional", "UF", "Fila", "Prioridade", "Status_Maestro", "Faixa_Aging"],
    },
}

ESTADO_MEMORIA: Dict[str, Dict[str, Any]] = {}


def obter_modo_ambiente() -> str:
    return os.getenv("ENV_MODE", "MOCK").upper()


def _descobrir_colunas_filtraveis(df: pd.DataFrame, sugeridas: list) -> Dict[str, list]:
    """
    Descobre automaticamente quais colunas têm valores categóricos (até 40 valores únicos)
    para criar os seletores de filtro específicos de cada relatório, mesmo quando a planilha
    ou JSON mudar de colunas lá na Vivo!
    """
    if df.empty:
        return {}
    opcoes_filtro = {}
    colunas_ordenadas = [c for c in sugeridas if c in df.columns] + [
        c for c in df.columns if c not in sugeridas
    ]
    for col in colunas_ordenadas:
        valores_unicos = df[col].dropna().astype(str).unique().tolist()
        if 1 <= len(valores_unicos) <= 40 and not col.lower().startswith("id_"):
            opcoes_filtro[col] = sorted(valores_unicos)
            if len(opcoes_filtro) >= 6:
                break
    return opcoes_filtro


def carregar_relatorio(report_id: str) -> Dict[str, Any]:
    if report_id not in CATALOGO_RELATORIOS:
        raise ValueError("Relatório não encontrado.")

    meta = CATALOGO_RELATORIOS[report_id]
    modo = obter_modo_ambiente()

    try:
        df = meta["extrator"](modo)
        erro_msg = None
    except Exception as exc:
        df = pd.DataFrame()
        erro_msg = str(exc)

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ESTADO_MEMORIA[report_id] = {
        "df": df,
        "atualizado_em": agora,
        "erro": erro_msg,
    }
    return serializar_relatorio(report_id)


def serializar_relatorio(report_id: str) -> Dict[str, Any]:
    meta = CATALOGO_RELATORIOS[report_id]
    estado = ESTADO_MEMORIA.get(report_id)
    if not estado:
        return carregar_relatorio(report_id)

    df: pd.DataFrame = estado["df"]
    registros = df.fillna("").to_dict(orient="records") if not df.empty else []
    colunas = list(df.columns) if not df.empty else []
    filtros_disponiveis = _descobrir_colunas_filtraveis(df, meta["colunas_filtro_sugeridas"])

    return {
        "id": report_id,
        "nome": meta["nome"],
        "aba_excel": meta["aba_excel"],
        "origem": meta["origem"],
        "atualizado_em": estado["atualizado_em"],
        "erro": estado["erro"],
        "colunas": colunas,
        "registros": registros,
        "filtros_disponiveis": filtros_disponiveis,
    }


def inicializar_dados():
    for rep_id in CATALOGO_RELATORIOS:
        carregar_relatorio(rep_id)


@app.route("/")
def index():
    caminho_html = os.path.join(os.path.dirname(__file__), "src", "static", "index.html")
    with open(caminho_html, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/api/state", methods=["GET"])
def obter_estado_completo():
    return jsonify({
        "modo_ambiente": obter_modo_ambiente(),
        "relatorios": {rep_id: serializar_relatorio(rep_id) for rep_id in CATALOGO_RELATORIOS},
    })


@app.route("/api/extract-all", methods=["POST"])
def extrair_todos_relatorios():
    for rep_id in CATALOGO_RELATORIOS:
        carregar_relatorio(rep_id)
    return obter_estado_completo()


@app.route("/api/extract/<report_id>", methods=["POST"])
def extrair_relatorio_unico(report_id: str):
    if report_id not in CATALOGO_RELATORIOS:
        return jsonify({"detail": "Relatório não encontrado"}), 404
    return jsonify(carregar_relatorio(report_id))


@app.route("/api/upload/<report_id>", methods=["POST"])
def upload_planilha_manual(report_id: str):
    if report_id not in CATALOGO_RELATORIOS:
        return jsonify({"detail": "Relatório inválido."}), 404

    if "file" not in request.files:
        return jsonify({"detail": "Nenhum arquivo enviado."}), 400

    arq = request.files["file"]
    conteudo = arq.read()
    nome_arq = (arq.filename or "").lower()

    try:
        if nome_arq.endswith(".csv"):
            try:
                df = pd.read_csv(BytesIO(conteudo), sep=";", encoding="utf-8")
            except Exception:
                df = pd.read_csv(BytesIO(conteudo), sep=",", encoding="latin1")
        elif nome_arq.endswith(".json"):
            df = pd.read_json(BytesIO(conteudo))
        else:
            df = ler_xlsx_nativo(conteudo)
    except Exception as exc:
        return jsonify({"detail": f"Erro ao ler arquivo: {exc}"}), 400

    ESTADO_MEMORIA[report_id] = {
        "df": df,
        "atualizado_em": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (Arquivo: {arq.filename})",
        "erro": None,
    }
    return jsonify(serializar_relatorio(report_id))


def _aplicar_filtros_dataframe(
    df: pd.DataFrame, filtros: Dict[str, str], termo_busca: str
) -> pd.DataFrame:
    if df.empty:
        return df

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


@app.route("/api/export-excel", methods=["POST"])
def exportar_excel_unificado():
    payload = request.get_json(silent=True) or {}
    filtros_por_relatorio = payload.get("filtros_por_relatorio", {})
    busca_por_relatorio = payload.get("busca_por_relatorio", {})

    relatorios_para_excel = {}
    for rep_id, meta in CATALOGO_RELATORIOS.items():
        if rep_id not in ESTADO_MEMORIA:
            carregar_relatorio(rep_id)
        estado = ESTADO_MEMORIA[rep_id]
        df_bruto: pd.DataFrame = estado["df"]
        filtros_rep = filtros_por_relatorio.get(rep_id, {})
        busca_rep = busca_por_relatorio.get(rep_id, "")

        df_filtrado = _aplicar_filtros_dataframe(df_bruto, filtros_rep, busca_rep)

        filtros_descritivos = dict(filtros_rep)
        if busca_rep:
            filtros_descritivos["Busca"] = busca_rep

        relatorios_para_excel[rep_id] = {
            "nome": meta["nome"],
            "aba_excel": meta["aba_excel"],
            "origem": meta["origem"],
            "total_bruto": len(df_bruto),
            "df_filtrado": df_filtrado,
            "filtros": filtros_descritivos,
            "atualizado_em": estado["atualizado_em"],
        }

    xlsx_bytes = gerar_excel_unificado(relatorios_para_excel)
    nome_arquivo = f"Centralizador_Vivo_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"

    return send_file(
        BytesIO(xlsx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nome_arquivo,
    )


if __name__ == "__main__":
    inicializar_dados()
    print("==========================================================")
    print("  CENTRALIZADOR DE RELATORIOS VIVO RODANDO EM:")
    print("  -> http://127.0.0.1:8000")
    print("==========================================================")
    app.run(host="127.0.0.1", port=8000, debug=True)
