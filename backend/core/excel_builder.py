from io import BytesIO
from typing import Dict, Any, List
import zipfile
from xml.sax.saxutils import escape
import pandas as pd


def _col_letter(col_idx: int) -> str:
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
) -> str:
    views_xml = '<sheetViews><sheetView workbookViewId="0">'
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
        row_h = 24 if r_idx == 1 else 19
        sheet_data_xml += f'<row r="{r_idx}" ht="{row_h}" customHeight="1">'
        for c_idx, (val, st_id) in enumerate(row_cells, start=1):
            sheet_data_xml += _cell_xml(r_idx, c_idx, val, st_id)
        sheet_data_xml += "</row>"
    sheet_data_xml += "</sheetData>"

    filter_xml = f'<autoFilter ref="{auto_filter_ref}"/>' if auto_filter_ref else ""

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"{views_xml}"
        f"{cols_xml}"
        f"{sheet_data_xml}"
        f"{filter_xml}"
        "</worksheet>"
    )


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="3">
    <font><sz val="10"/><color rgb="FF1F2937"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF111827"/><name val="Calibri"/></font>
  </fonts>
  <fills count="4">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF660099"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8F9FA"/></patternFill></fill>
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
  <cellXfs count="5">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="2" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center"/>
    </xf>
  </cellXfs>
</styleSheet>"""


def _montar_aba_relatorio(df: pd.DataFrame) -> str:
    colunas = [c for c in list(df.columns) if c != "_row_idx"] if not df.empty else ["Status"]
    rows_data: List[List[tuple]] = []

    # Linha 1: Cabeçalho da Tabela em Roxo Vivo (#660099)
    rows_data.append([(str(c), 1) for c in colunas])

    if df.empty:
        return _build_sheet_xml(rows_data, [18] * len(colunas), freeze_row=1)

    larguras = [max(len(str(c)) + 5, 13) for c in colunas]
    for idx_r, (_, row) in enumerate(df.iterrows()):
        estilo = 3 if idx_r % 2 == 1 else 2
        linha = []
        for idx_c, col_name in enumerate(colunas):
            val = row[col_name]
            if pd.isna(val):
                val = ""
            primeira_linha = str(val).splitlines()[0] if str(val) else ""
            larguras[idx_c] = min(max(larguras[idx_c], len(primeira_linha) + 4), 45)
            linha.append((val, estilo))
        rows_data.append(linha)

    ultima_col = _col_letter(len(colunas))
    ultima_linha = 1 + len(df)
    auto_filter = f"A1:{ultima_col}{ultima_linha}"

    return _build_sheet_xml(
        rows_data=rows_data,
        col_widths=larguras,
        auto_filter_ref=auto_filter,
        freeze_row=1,
    )


def gerar_excel_unificado(relatorios_info: Dict[str, Dict[str, Any]]) -> bytes:
    """
    Gera o arquivo Excel (.xlsx) contendo EXCLUSIVAMENTE as 3 abas dos relatórios diários
    (O Resumo fica apenas na plataforma online!):
    - Aba 1: P1
    - Aba 2: AnelComutado
    - Aba 3: CellDowntime
    """
    abas = []
    for rep_id, info in relatorios_info.items():
        xml_aba = _montar_aba_relatorio(df=info["df_filtrado"])
        abas.append((info["aba_excel"][:31], xml_aba))

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
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

        rels_root = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            "</Relationships>"
        )
        zf.writestr("_rels/.rels", rels_root)

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
        zf.writestr("xl/styles.xml", _styles_xml())

        for i, (_, xml_content) in enumerate(abas, start=1):
            zf.writestr(f"xl/worksheets/sheet{i}.xml", xml_content)

    buffer.seek(0)
    return buffer.read()
