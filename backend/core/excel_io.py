from io import BytesIO
from datetime import datetime, timedelta
from typing import Union, Optional, List
import zipfile
import xml.etree.ElementTree as ET
import re
import pandas as pd


def _col_str_to_idx(col_str: str) -> int:
    idx = 0
    for ch in col_str:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def converter_serial_excel_para_data(valor: Union[str, float, int]) -> str:
    if valor is None or valor == "":
        return ""
    s = str(valor).strip()
    if not s:
        return ""
    try:
        num = float(s)
        if 35000 <= num <= 60000:
            dt = datetime(1899, 12, 30) + timedelta(days=num)
            return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        pass
    return s


def listar_abas_xlsx(fonte: Union[str, bytes, BytesIO]) -> List[str]:
    if isinstance(fonte, bytes):
        fonte = BytesIO(fonte)
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(fonte, "r") as zf:
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        return [sh.attrib.get("name", "") for sh in wb.findall(".//main:sheet", ns)]


def ler_xlsx_nativo(
    fonte: Union[str, bytes, BytesIO],
    sheet_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Leitor nativo de arquivos .xlsx / .xlsm (OpenXML) em Python puro.
    Suporta células com referência explícita ('A1') e células posicionais do Power BI.
    """
    if isinstance(fonte, bytes):
        fonte = BytesIO(fonte)

    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(fonte, "r") as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in ss_root.findall("main:si", ns):
                textos = [t.text or "" for t in si.findall(".//main:t", ns)]
                shared_strings.append("".join(textos))

        target_sheet_path = None
        if "xl/workbook.xml" in zf.namelist() and "xl/_rels/workbook.xml.rels" in zf.namelist():
            rels = {
                el.attrib["Id"]: el.attrib["Target"]
                for el in ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
            }
            wb = ET.fromstring(zf.read("xl/workbook.xml"))
            for sh in wb.findall(".//main:sheet", ns):
                nome_aba = sh.attrib.get("name", "")
                rid = sh.attrib.get(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", ""
                )
                caminho = "xl/" + rels.get(rid, "").lstrip("/")
                if sheet_name is None and caminho.startswith("xl/worksheets/"):
                    target_sheet_path = caminho
                    break
                if sheet_name and nome_aba.lower() == sheet_name.lower():
                    target_sheet_path = caminho
                    break

        if not target_sheet_path or target_sheet_path not in zf.namelist():
            sheet_files = sorted(
                [f for f in zf.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
            )
            if not sheet_files:
                return pd.DataFrame()
            target_sheet_path = sheet_files[0]

        sheet_root = ET.fromstring(zf.read(target_sheet_path))
        rows_parsed = []
        max_col = 0

        for row_el in sheet_root.findall(".//main:sheetData/main:row", ns):
            row_dict = {}
            next_pos_col = 0
            for c_el in row_el.findall("main:c", ns):
                ref = c_el.attrib.get("r", "")
                if ref:
                    m = re.match(r"([A-Za-z]+)", ref)
                    col_idx = _col_str_to_idx(m.group(1)) if m else next_pos_col
                else:
                    col_idx = next_pos_col
                next_pos_col = col_idx + 1
                max_col = max(max_col, col_idx)

                c_type = c_el.attrib.get("t", "")
                v_el = c_el.find("main:v", ns)
                is_el = c_el.find("main:is", ns)

                val = ""
                if c_type == "s" and v_el is not None and v_el.text is not None:
                    s_idx = int(v_el.text)
                    val = shared_strings[s_idx] if s_idx < len(shared_strings) else ""
                elif c_type == "inlineStr" and is_el is not None:
                    val = "".join([t.text or "" for t in is_el.findall(".//main:t", ns)])
                elif v_el is not None and v_el.text is not None:
                    val = v_el.text

                row_dict[col_idx] = val
            if row_dict:
                rows_parsed.append(row_dict)

        if not rows_parsed:
            return pd.DataFrame()

        matriz = []
        for r_dict in rows_parsed:
            linha = [r_dict.get(i, "") for i in range(max_col + 1)]
            if any(str(x).strip() != "" for x in linha):
                matriz.append(linha)

        if not matriz:
            return pd.DataFrame()

        idx_cabecalho = 0
        for i, linha in enumerate(matriz[:5]):
            preenchidas = sum(1 for x in linha if str(x).strip() != "")
            if preenchidas >= 3:
                idx_cabecalho = i
                break

        cabecalho_bruto = matriz[idx_cabecalho]
        cabecalho = []
        vistos = {}
        for i, c in enumerate(cabecalho_bruto):
            nome = str(c).strip() or f"Coluna_{i+1}"
            if nome in vistos:
                vistos[nome] += 1
                nome = f"{nome}_{vistos[nome]}"
            else:
                vistos[nome] = 1
            cabecalho.append(nome)

        dados = matriz[idx_cabecalho + 1:]
        dados_limpos = [
            linha for linha in dados
            if sum(1 for x in linha if str(x).strip() != "") >= 2
        ]
        return pd.DataFrame(dados_limpos, columns=cabecalho)
