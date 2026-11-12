import os
from typing import Dict, List, Any
import pandas as pd
import requests
from backend.core.excel_io import converter_serial_excel_para_data, ler_xlsx_nativo

COLUNAS_FORMATADAS_P1 = [
    "uf",
    "ddd",
    "municipio",
    "ticket",
    "sigla_erb",
    "data_falha",
    "grupo_responsavel",
    "técnico",
    "data",
    "status atualizado",
]


def autenticar_domus(base_url: str, username: str, password: str, verify_ssl: bool = False) -> str:
    url_login = f"{base_url.rstrip('/')}/auth/login"
    resp = requests.post(
        url_login,
        json={"username": username, "password": password},
        verify=verify_ssl,
        timeout=30,
    )
    resp.raise_for_status()

    try:
        dados = resp.json()
        if isinstance(dados, dict):
            for k in ("token", "access_token", "x-access-token", "jwt"):
                if k in dados and dados[k]:
                    return str(dados[k]).strip()
        if isinstance(dados, str):
            return dados.strip()
    except Exception:
        pass

    return resp.text.strip().strip('"')


def consultar_calamidade_details(
    base_url: str,
    token: str,
    filtros_api: Dict[str, Any] = None,
    verify_ssl: bool = False,
) -> List[Dict[str, Any]]:
    url_query = f"{base_url.rstrip('/')}/query/calamidade-details"
    headers = {"x-access-token": token, "Accept": "application/json"}

    params = {
        "page": 0,
        "limit": 5000,
        "mode": os.getenv("DOMUS_MODE", "tickets"),
        "detail_type": os.getenv("DOMUS_DETAIL_TYPE", "sites_fora"),
    }
    if filtros_api:
        for k in ("page", "limit", "mode", "detail_type", "uf", "ddd", "municipio", "site", "tecnologia"):
            if k in filtros_api and filtros_api[k]:
                params[k] = filtros_api[k]

    resp = requests.get(url_query, headers=headers, params=params, verify=verify_ssl, timeout=60)
    resp.raise_for_status()
    dados = resp.json()

    if isinstance(dados, list):
        return dados
    if isinstance(dados, dict):
        for chave in ("data", "items", "result", "results", "registros", "rows", "value"):
            if chave in dados and isinstance(dados[chave], list):
                return dados[chave]
        return [dados]
    return []


def carregar_p1_bruto_local() -> pd.DataFrame:
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    caminho_csv = os.path.join(raiz, "bruto", "p1.csv")
    caminho_xlsx = os.path.join(raiz, "formatado", "p1.xlsx")

    if os.path.exists(caminho_csv):
        try:
            return pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
        except Exception:
            return pd.read_csv(caminho_csv, sep=";", encoding="latin1")
    if os.path.exists(caminho_xlsx):
        return ler_xlsx_nativo(caminho_xlsx)
    return pd.DataFrame(columns=COLUNAS_FORMATADAS_P1)


def formatar_p1_domus(df_bruto: pd.DataFrame) -> pd.DataFrame:
    if df_bruto is None or df_bruto.empty:
        return pd.DataFrame(columns=COLUNAS_FORMATADAS_P1)

    df = df_bruto.copy()
    mapa_lower = {c.lower().strip(): c for c in df.columns}

    saida = pd.DataFrame()
    for col_alvo in COLUNAS_FORMATADAS_P1:
        col_origem = mapa_lower.get(col_alvo.lower())
        if not col_origem and col_alvo == "técnico":
            col_origem = mapa_lower.get("tecnico")
        if col_origem and col_origem in df.columns:
            saida[col_alvo] = df[col_origem].fillna("").astype(str)
        else:
            saida[col_alvo] = ""

    if "data_falha" in saida.columns:
        saida["data_falha"] = saida["data_falha"].apply(converter_serial_excel_para_data)

    return saida


def extrair_p1_domus(modo_ambiente: str = "MOCK", filtros_api: Dict[str, Any] = None) -> pd.DataFrame:
    if modo_ambiente.upper() == "PROD":
        base_url = os.getenv("DOMUS_BASE_URL", "http://10.215.39.118:8001").strip()
        username = os.getenv("DOMUS_USERNAME", "regional_norte").strip()
        password = os.getenv("DOMUS_PASSWORD", "").strip()
        token_fixo = os.getenv("DOMUS_API_TOKEN", "").strip()
        verify_ssl = os.getenv("DOMUS_VERIFY_SSL", "False").lower() == "true"

        token = token_fixo
        if password:
            try:
                token = autenticar_domus(base_url, username, password, verify_ssl=verify_ssl)
            except Exception:
                if not token_fixo:
                    raise

        if token:
            registros = consultar_calamidade_details(
                base_url, token, filtros_api=filtros_api, verify_ssl=verify_ssl
            )
            df_api = pd.json_normalize(registros) if registros else pd.DataFrame()
            return formatar_p1_domus(df_api)

    df_bruto = carregar_p1_bruto_local()
    return formatar_p1_domus(df_bruto)
