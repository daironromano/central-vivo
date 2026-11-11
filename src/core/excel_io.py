from io import BytesIO
from typing import Union
import zipfile
import xml.etree.ElementTree as ET
import re
import pandas as pd


def _col_str_to_idx(col_str: str) -> int:
    idx = 0
    for ch in col_str:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def ler_xlsx_nativo(fonte: Union[str, bytes, BytesIO]) -> pd.DataFrame:
    """
    Leitor nativo de arquivos .xlsx (OpenXML) usando apenas bibliotecas padrão do Python.
    Garante que o sistema leia planilhas Excel mesmo se 'openpyxl' não estiver instalado
    no computador da Vivo!
    """
    if isinstance(fonte, bytes):
        fonte = BytesIO(fonte)

    try:
        return pd.read_excel(fonte)
    except Exception:
        if isinstance(fonte, BytesIO):
            fonte.seek(0)

    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(fonte, "r") as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in ss_root.findall("main:si", ns):
                textos = [t.text or "" for t in si.findall(".//main:t", ns)]
                shared_strings.append("".join(textos))

        sheet_files = sorted(
            [f for f in zf.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
        )
        if not sheet_files:
            return pd.DataFrame()

        sheet_root = ET.fromstring(zf.read(sheet_files[0]))
        rows_parsed = []
        max_col = 0

        for row_el in sheet_root.findall(".//main:sheetData/main:row", ns):
            row_dict = {}
            for c_el in row_el.findall("main:c", ns):
                ref = c_el.attrib.get("r", "A1")
                m = re.match(r"([A-Za-z]+)", ref)
                col_idx = _col_str_to_idx(m.group(1)) if m else 0
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

        cabecalho = [str(c).strip() or f"Coluna_{i+1}" for i, c in enumerate(matriz[0])]
        dados = matriz[1:]
        return pd.DataFrame(dados, columns=cabecalho)
