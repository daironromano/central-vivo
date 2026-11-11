from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List
import zipfile
from xml.sax.saxutils import escape
import pandas as pd


def _col_letter(col_idx: int) -> str:
    """Converte índice 1-based (1=A, 2=B, ..., 27=AA) para letra de coluna do Excel."""
    result = ""
    while col_idx > 0:
        col_idx, rem = divmod(col_idx - 1, 26)
        result = chr(65 + rem) + result
    return result


def _cell_xml(row_idx: int, col_idx: int, val: Any, style_id: int = 0) -> str:
    ref = f"{_col_letter(col_idx)}{row_idx}"
    if val is None or (isinstance(val, float) and pd.isna(val)):
        val = ""
    if isinstance(val, bool):
        return f'<c r="{ref}" s="{style_id}" t="inlineStr"><is><t>{str(val)}</t></is></c>'
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return f'<c r="{ref}" s="{style_id}"><v>{val}</v></c>'
    texto = escape(str(val))
    return f'<c r="{ref}" s="{style_id}" t="inlineStr"><is><t xml:space="preserve">{texto}</t></is></c>'


def _build_sheet_xml(
    rows_data: List[List[tuple]],
    col_widths: List[int],
    auto_filter_ref: str = "",
    freeze_row: int = 0,
    merged_ranges: List[str] = None,
) -> str:
    """
    Constrói o XML nativo de uma aba do Excel (.xlsx OpenXML) com estilos,
    larguras de coluna, congelamento de painel (freeze panes) e AutoFiltro nativo.
    Funciona sem precisar instalar bibliotecas externas caso o proxy da Vivo bloqueie pip!
    """
    views_xml = "<sheetViews><sheetView workbookViewId=\"0\">"
    if freeze_row > 0:
        views_xml += (
            f'<pane ySplit="{freeze_row}" topLeftCell="A{freeze_row + 1}" '
            f'activePane="bottomLeft" state="frozen"/>'
        )
    views_xml += "</sheetView></sheetViews>"

    cols_xml = "<cols>"
    for idx, w in enumerate(col_widths, start=1):
        cols_xml += f'<col min="{idx}" max="{idx}" width="{w}" customWidth="1"/>'
    cols_xml += "</cols>"

    sheet_data_xml = "<sheetData>"
    for r_idx, row_cells in enumerate(rows_data, start=1):
        if not row_cells:
            continue
        # Verifica se há altura customizada na linha
        row_h = 26 if r_idx == 1 else (22 if any(st in (1, 2) for _, st in row_cells) else 19)
        sheet_data_xml += f'<row r="{r_idx}" ht="{row_h}" customHeight="1">'
        for c_idx, (val, st_id) in enumerate(row_cells, start=1):
            sheet_data_xml += _cell_xml(r_idx, c_idx, val, st_id)
        sheet_data_xml += "</row>"
    sheet_data_xml += "</sheetData>"

    merge_xml = ""
    if merged_ranges:
        merge_xml = f'<mergeCells count="{len(merged_ranges)}">'
        for mr in merged_ranges:
            merge_xml += f'<mergeCell ref="{mr}"/>'
        merge_xml += "</mergeCells>"

    filter_xml = f'<autoFilter ref="{auto_filter_ref}"/>' if auto_filter_ref else ""

    # Ordem estrita exigida pelo schema OpenXML:
    # sheetViews -> cols -> sheetData -> autoFilter -> mergeCells
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"{views_xml}"
        f"{cols_xml}"
        f"{sheet_data_xml}"
        f"{filter_xml}"
        f"{merge_xml}"
        "</worksheet>"
    )


def _styles_xml() -> str:
    """
    Folha de estilos OpenXML com a identidade visual da Vivo:
    style 0: Normal
    style 1: Banner Vivo Roxo (#660099), fonte branca 13pt negrito
    style 2: Cabeçalho Tabela (#2D1147), fonte branca 10pt negrito + borda
    style 3: Linha de Dados Branca com borda
    style 4: Linha de Dados Zebra (#F8F9FA) com borda
    style 5: Subtítulo / Totalizador Lilás Claro (#F3E5F5), negrito + borda
    style 6: Título de Seção Roxo Vivo (#660099), 11pt negrito
    style 7: Subtítulo Itálico Cinza (Filtros aplicados)
    """
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="6">
    <font><sz val="10"/><color rgb="FF1F2937"/><name val="Calibri"/></font>
    <font><b/><sz val="13"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF111827"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><color rgb="FF660099"/><name val="Calibri"/></font>
    <font><i/><sz val="9"/><color rgb="FF4B5563"/><name val="Calibri"/></font>
  </fonts>
  <fills count="6">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF660099"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF2D1147"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8F9FA"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF3E5F5"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFD1D5DB"/></left>
      <right style="thin"><color rgb="FFD1D5DB"/></right>
      <top style="thin"><color rgb="FFD1D5DB"/></top>
      <bottom style="thin"><color rgb="FFD1D5DB"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="8">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="3" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1"/>
    <xf numFmtId="0" fontId="5" fillId="0" borderId="0" xfId="0" applyFont="1"/>
  </cellXfs>
</styleSheet>"""


def _montar_aba_relatorio(
    nome_relatorio: str, df: pd.DataFrame, filtros_ativos: Dict[str, str]
) -> str:
    colunas = list(df.columns) if not df.empty else ["Status"]
    num_cols = max(len(colunas), 4)

    resumo_filtros = (
        ", ".join([f"{k}: {v}" for k, v in filtros_ativos.items() if v and v != "TODOS"])
        if filtros_ativos
        else "Nenhum filtro restritivo (Exibindo base completa)"
    )

    rows_data: List[List[tuple]] = []

    # Linha 1: Banner Roxo Vivo
    row1 = [(f"{nome_relatorio} — Total: {len(df)} registros", 1)] + [("", 1) for _ in range(num_cols - 1)]
    rows_data.append(row1)

    # Linha 2: Subtítulo com os filtros aplicados nesta aba
    row2 = [(f"Filtros aplicados nesta aba: {resumo_filtros}", 7)] + [("", 7) for _ in range(num_cols - 1)]
    rows_data.append(row2)

    # Linha 3: Espaço em branco
    rows_data.append([])

    merged = [
        f"A1:{_col_letter(num_cols)}1",
        f"A2:{_col_letter(num_cols)}2",
    ]

    if df.empty:
        rows_data.append([("Nenhum registro encontrado para os filtros selecionados.", 0)])
        return _build_sheet_xml(rows_data, [25] * num_cols, merged_ranges=merged)

    # Linha 4: Cabeçalho da Tabela
    rows_data.append([(str(c), 2) for c in colunas])

    # Linhas de Dados (5 em diante)
    larguras = [max(len(str(c)) + 5, 14) for c in colunas]
    for idx_r, (_, row) in enumerate(df.iterrows()):
        estilo = 4 if idx_r % 2 == 1 else 3
        linha = []
        for idx_c, col_name in enumerate(colunas):
            val = row[col_name]
            if pd.isna(val):
                val = ""
            larguras[idx_c] = min(max(larguras[idx_c], len(str(val)) + 4), 45)
            linha.append((val, estilo))
        rows_data.append(linha)

    ultima_col = _col_letter(len(colunas))
    ultima_linha = 4 + len(df)
    auto_filter = f"A4:{ultima_col}{ultima_linha}"

    return _build_sheet_xml(
        rows_data=rows_data,
        col_widths=larguras,
        auto_filter_ref=auto_filter,
        freeze_row=4,
        merged_ranges=merged,
    )


def _montar_aba_resumo(relatorios_info: Dict[str, Dict[str, Any]]) -> str:
    rows_data: List[List[tuple]] = []

    # Linha 1: Banner Principal
    titulo = f"VIVO — RESUMO EXECUTIVO DIÁRIO DE RELATÓRIOS ({datetime.now().strftime('%d/%m/%Y %H:%M')})"
    rows_data.append([(titulo, 1)] + [("", 1) for _ in range(5)])
    rows_data.append([])

    # Seção 1: Visão Consolidada
    rows_data.append([("1. VISÃO CONSOLIDADA DOS SISTEMAS", 6)])
    headers_visao = [
        "Relatório / Sistema",
        "Origem",
        "Total Bruto",
        "Total Filtrado (Na Aba)",
        "Filtros Aplicados",
        "Última Atualização",
    ]
    rows_data.append([(h, 2) for h in headers_visao])

    soma_bruto = 0
    soma_filtrado = 0
    for rep_id, info in relatorios_info.items():
        df_f: pd.DataFrame = info["df_filtrado"]
        bruto = info["total_bruto"]
        filtros = info.get("filtros", {})
        txt_filtros = ", ".join([f"{k}={v}" for k, v in filtros.items() if v and v != "TODOS"]) or "Todos"

        soma_bruto += bruto
        soma_filtrado += len(df_f)

        rows_data.append([
            (info["nome"], 3),
            (info["origem"], 3),
            (bruto, 3),
            (len(df_f), 3),
            (txt_filtros, 3),
            (info.get("atualizado_em", "-"), 3),
        ])

    rows_data.append([
        ("TOTAL CONSOLIDADO", 5),
        ("-", 5),
        (soma_bruto, 5),
        (soma_filtrado, 5),
        ("-", 5),
        (datetime.now().strftime("%H:%M"), 5),
    ])
    rows_data.append([])

    # Seção 2: Matriz Consolidada por Regional
    rows_data.append([("2. MATRIZ CONSOLIDADA POR REGIONAL (P1 DOMUS x ANEL COMUTADO x BACKLOG MAESTRO)", 6)])
    nomes_reps = [info["nome"] for info in relatorios_info.values()]
    headers_reg = ["Regional"] + nomes_reps + ["Total na Regional"]
    rows_data.append([(h, 2) for h in headers_reg])

    regionais_set = set()
    contagens_por_rep = {}
    for rep_id, info in relatorios_info.items():
        df_f = info["df_filtrado"]
        col_reg = next((c for c in df_f.columns if "regional" in c.lower() or c.lower() == "uf"), None)
        if col_reg and not df_f.empty:
            contagem = df_f[col_reg].astype(str).value_counts().to_dict()
            regionais_set.update(contagem.keys())
            contagens_por_rep[rep_id] = contagem
        else:
            contagens_por_rep[rep_id] = {}

    for reg in sorted(regionais_set):
        linha_reg = [(reg, 3)]
        tot_reg = 0
        for rep_id in relatorios_info.keys():
            qtd = int(contagens_por_rep.get(rep_id, {}).get(reg, 0))
            tot_reg += qtd
            linha_reg.append((qtd, 3))
        linha_reg.append((tot_reg, 5))
        rows_data.append(linha_reg)

    rows_data.append([])

    # Seção 3: Quebra por Status de cada Relatório
    rows_data.append([("3. QUEBRA POR STATUS / SITUAÇÃO DE CADA RELATÓRIO", 6)])
    for rep_id, info in relatorios_info.items():
        df_f = info["df_filtrado"]
        col_status = next(
            (c for c in df_f.columns if any(k in c.lower() for k in ["status", "situacao", "severidade", "prioridade"])),
            None,
        )
        if col_status and not df_f.empty:
            rows_data.append([(f"{info['nome']} (por {col_status})", 5), ("Quantidade", 5)])
            for st_val, qtd in df_f[col_status].astype(str).value_counts().items():
                rows_data.append([(str(st_val), 3), (int(qtd), 3)])
            rows_data.append([])

    return _build_sheet_xml(
        rows_data=rows_data,
        col_widths=[34, 26, 26, 26, 32, 24],
        merged_ranges=["A1:F1"],
    )


def gerar_excel_unificado(relatorios_info: Dict[str, Dict[str, Any]]) -> bytes:
    """
    Gera o arquivo Excel (.xlsx) completo com 4 abas:
    1. Resumo Geral
    2. P1_DOMUS (com filtros aplicados + AutoFiltro Excel)
    3. Anel_Comutado (com filtros aplicados + AutoFiltro Excel)
    4. Backlog_Maestro (com filtros aplicados + AutoFiltro Excel)
    """
    abas = [("Resumo Geral", _montar_aba_resumo(relatorios_info))]
    for rep_id, info in relatorios_info.items():
        xml_aba = _montar_aba_relatorio(
            nome_relatorio=info["nome"],
            df=info["df_filtrado"],
            filtros_ativos=info.get("filtros", {}),
        )
        abas.append((info["aba_excel"][:31], xml_aba))

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        sheets_ct = "".join(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for i in range(1, len(abas) + 1)
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            f"{sheets_ct}"
            "</Types>"
        )
        zf.writestr("[Content_Types].xml", content_types)

        # _rels/.rels
        rels_root = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            "</Relationships>"
        )
        zf.writestr("_rels/.rels", rels_root)

        # xl/workbook.xml
        sheets_wb = "".join(
            f'<sheet name="{escape(nome)}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (nome, _) in enumerate(abas, start=1)
        )
        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f"<sheets>{sheets_wb}</sheets>"
            "</workbook>"
        )
        zf.writestr("xl/workbook.xml", workbook_xml)

        # xl/_rels/workbook.xml.rels
        rels_wb = "".join(
            f'<Relationship Id="rId{i}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(abas) + 1)
        )
        rels_wb += (
            f'<Relationship Id="rId{len(abas) + 1}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
            'Target="styles.xml"/>'
        )
        workbook_rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f"{rels_wb}"
            "</Relationships>"
        )
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)

        # xl/styles.xml
        zf.writestr("xl/styles.xml", _styles_xml())

        # xl/worksheets/sheet1..N.xml
        for i, (_, xml_content) in enumerate(abas, start=1):
            zf.writestr(f"xl/worksheets/sheet{i}.xml", xml_content)

    buffer.seek(0)
    return buffer.read()
