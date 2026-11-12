from io import BytesIO
from datetime import datetime
import pandas as pd
from flask import Blueprint, request, jsonify, send_file, render_template, g

from src.models.report_model import ReportModel, CATALOGO_RELATORIOS
from src.core.excel_builder import gerar_excel_unificado
from src.core.excel_io import ler_xlsx_nativo
from src.core.security import exigir_autenticacao, registrar_auditoria

report_bp = Blueprint("report_bp", __name__)
report_model = ReportModel()


@report_bp.route("/", methods=["GET"])
@exigir_autenticacao()
def dashboard_principal():
    return render_template("dashboard.html")


@report_bp.route("/api/state", methods=["GET"])
@exigir_autenticacao()
def obter_estado_completo():
    u = g.usuario_atual
    return jsonify({
        "modo_ambiente": report_model.obter_modo_ambiente(),
        "usuario": {
            "username": u.get("sub"),
            "nome": u.get("nome"),
            "perfil": u.get("perfil"),
            "csrf_token": u.get("csrf"),
        },
        "relatorios": {
            rep_id: report_model.serializar_relatorio(rep_id)
            for rep_id in CATALOGO_RELATORIOS
        },
    })


@report_bp.route("/api/extract-all", methods=["POST"])
@exigir_autenticacao()
def extrair_todos_relatorios():
    for rep_id in CATALOGO_RELATORIOS:
        report_model.carregar_relatorio(rep_id)
    u = g.usuario_atual
    registrar_auditoria("EXTRAIR_TODOS", u.get("sub", ""), u.get("perfil", ""), "Sincronizou P1, Anel e CellDowntime")
    return obter_estado_completo()


@report_bp.route("/api/extract/<report_id>", methods=["POST"])
@exigir_autenticacao()
def extrair_relatorio_unico(report_id: str):
    if report_id not in CATALOGO_RELATORIOS:
        return jsonify({"detail": "Relatório não encontrado."}), 404
    dados = report_model.carregar_relatorio(report_id)
    u = g.usuario_atual
    registrar_auditoria("EXTRAIR_RELATORIO", u.get("sub", ""), u.get("perfil", ""), f"Sincronizou {report_id}")
    return jsonify(dados)


@report_bp.route("/api/upload/<report_id>", methods=["POST"])
@exigir_autenticacao(perfis_permitidos=["administrador"])
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
                df_bruto = pd.read_csv(BytesIO(conteudo), sep=";", encoding="utf-8")
            except Exception:
                df_bruto = pd.read_csv(BytesIO(conteudo), sep=",", encoding="latin1")
        elif nome_arq.endswith(".json"):
            df_bruto = pd.read_json(BytesIO(conteudo))
        else:
            df_bruto = ler_xlsx_nativo(conteudo)
    except Exception as exc:
        return jsonify({"detail": f"Erro ao ler arquivo: {exc}"}), 400

    dados = report_model.importar_dataframe(report_id, df_bruto, f"Upload: {arq.filename}")
    u = g.usuario_atual
    registrar_auditoria(
        "UPLOAD_BASE_BRUTA",
        u.get("sub", ""),
        u.get("perfil", ""),
        f"Importou '{arq.filename}' em {report_id} ({len(dados['registros'])} linhas formatadas)",
    )
    return jsonify(dados)


@report_bp.route("/api/enm-cli/import", methods=["POST"])
@exigir_autenticacao()
def importar_cli_enm():
    payload = request.get_json(silent=True) or {}
    fonte = payload.get("fonte", "P1")
    texto = payload.get("texto", "")
    try:
        dados = report_model.importar_cli_enm_colado(fonte, texto)
        u = g.usuario_atual
        registrar_auditoria(
            "IMPORTAR_CLI_ENM",
            u.get("sub", ""),
            u.get("perfil", ""),
            f"Processou saída CLI ENM ({fonte}) com VLOOKUP automático",
        )
        return jsonify(dados)
    except ValueError as exc:
        return jsonify({"detail": str(exc)}), 400


@report_bp.route("/api/cell-edit", methods=["POST"])
@exigir_autenticacao()
def editar_celula_operacional():
    payload = request.get_json(silent=True) or {}
    rep_id = payload.get("report_id", "")
    row_idx = int(payload.get("row_idx", -1))
    coluna = payload.get("coluna", "")
    valor = payload.get("valor", "")

    ok = report_model.atualizar_celula(rep_id, row_idx, coluna, valor)
    if not ok:
        return jsonify({"detail": "Não foi possível atualizar a célula."}), 400
    return jsonify({"status": "ok"})


@report_bp.route("/api/export-excel", methods=["POST"])
@exigir_autenticacao()
def exportar_excel_unificado():
    payload = request.get_json(silent=True) or {}
    filtros_por_relatorio = payload.get("filtros_por_relatorio", {})
    busca_por_relatorio = payload.get("busca_por_relatorio", {})

    relatorios_para_excel = {}
    for rep_id, meta in CATALOGO_RELATORIOS.items():
        if rep_id not in report_model.estado_memoria:
            report_model.carregar_relatorio(rep_id)
        estado = report_model.estado_memoria[rep_id]
        df_bruto: pd.DataFrame = estado["df"]
        filtros_rep = filtros_por_relatorio.get(rep_id, {})
        busca_rep = busca_por_relatorio.get(rep_id, "")

        df_filtrado = report_model.aplicar_filtros_dataframe(df_bruto, filtros_rep, busca_rep)

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

    u = g.usuario_atual
    registrar_auditoria("EXPORTAR_EXCEL", u.get("sub", ""), u.get("perfil", ""), f"Baixou {nome_arquivo}")

    return send_file(
        BytesIO(xlsx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nome_arquivo,
    )
