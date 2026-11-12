import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import requests


def buscar_json_domus_real() -> List[Dict[str, Any]]:
   BASE_URL = os.getenv(
    "DOMUS_URL",
    "http://10.215.39.118:8001"
)

USUARIO = os.getenv("regional_norte")
SENHA = os.getenv("DOMUS_PASSWORD")

def obter_token():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "login": USUARIO,
            "senha": SENHA
        },
        timeout=60
    )

    resp.raise_for_status()

    dados = resp.json()

    return dados["token"]


def buscar_json_domus_real(
    mode="alarms",
    detail_type="sites_fora"
):
    token = obter_token()

    headers = {
        "x-access-token": token
    }

    params = {
        "page": 0,
        "limit": 50000,
        "mode": mode,
        "detail_type": detail_type
    }

    resp = requests.get(
        f"{BASE_URL}/query/calamidade-details",
        headers=headers,
        params=params,
        timeout=120
    )

    resp.raise_for_status()

    return resp.json()


def extrair_p1_domus(env_mode):
    dados = buscar_json_domus_real()

    if isinstance(dados, dict):
        if "data" in dados:
            dados = dados["data"]

    return pd.DataFrame(dados)


def gerar_mock_domus() -> pd.DataFrame:
    """
    Dados simulados de P1 (DOMUS) para testes fora da rede da Vivo.
    Assim que seu script real rodar, as colunas reais substituirão estas automaticamente!
    """
    hoje = datetime.now()
    dados = [
        {
            "ID_Chamado": "DOM-90811",
            "Tipo": "P1",
            "Regional": "SP",
            "UF": "SP",
            "Municipio": "São Paulo",
            "Site_Estacao": "ESP-SPO-014",
            "Status": "Em Atendimento",
            "Causa_Raiz": "Rompimento Fibra Óptica",
            "Impacto_Clientes": 1450,
            "SLA_Status": "Dentro do Prazo",
            "Data_Abertura": (hoje - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "NOC Nível 2",
        },
        {
            "ID_Chamado": "DOM-90815",
            "Tipo": "P1",
            "Regional": "SUL",
            "UF": "PR",
            "Municipio": "Curitiba",
            "Site_Estacao": "EPR-CWB-008",
            "Status": "Pendente Campo",
            "Causa_Raiz": "Falha de Energia / AC",
            "Impacto_Clientes": 3200,
            "SLA_Status": "Crítico",
            "Data_Abertura": (hoje - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "Equipe Campo Sul",
        },
        {
            "ID_Chamado": "DOM-90822",
            "Tipo": "P1",
            "Regional": "NE",
            "UF": "PE",
            "Municipio": "Recife",
            "Site_Estacao": "EPE-REC-042",
            "Status": "Em Atendimento",
            "Causa_Raiz": "Placa Transmissora",
            "Impacto_Clientes": 890,
            "SLA_Status": "Dentro do Prazo",
            "Data_Abertura": (hoje - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "Engenharia TX",
        },
        {
            "ID_Chamado": "DOM-90830",
            "Tipo": "P1",
            "Regional": "RJ/ES",
            "UF": "RJ",
            "Municipio": "Rio de Janeiro",
            "Site_Estacao": "ERJ-RJO-102",
            "Status": "Encerrado",
            "Causa_Raiz": "Vandalismo",
            "Impacto_Clientes": 2100,
            "SLA_Status": "Dentro do Prazo",
            "Data_Abertura": (hoje - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "Equipe Campo RJ",
        },
        {
            "ID_Chamado": "DOM-90841",
            "Tipo": "P1",
            "Regional": "SP",
            "UF": "SP",
            "Municipio": "Campinas",
            "Site_Estacao": "ESP-CPS-019",
            "Status": "Pendente Campo",
            "Causa_Raiz": "Rompimento Fibra Óptica",
            "Impacto_Clientes": 4120,
            "SLA_Status": "Crítico",
            "Data_Abertura": (hoje - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "Equipe Fibra SP",
        },
        {
            "ID_Chamado": "DOM-90849",
            "Tipo": "P1",
            "Regional": "MG",
            "UF": "MG",
            "Municipio": "Belo Horizonte",
            "Site_Estacao": "EMG-BHE-055",
            "Status": "Em Atendimento",
            "Causa_Raiz": "Falha Equipamento Core",
            "Impacto_Clientes": 1780,
            "SLA_Status": "Dentro do Prazo",
            "Data_Abertura": (hoje - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "Responsavel": "NOC Nível 2",
        },
    ]
    return pd.DataFrame(dados)


def extrair_p1_domus(modo_ambiente: str = "MOCK") -> pd.DataFrame:
    """
    Executa a extração do relatório P1 (DOMUS).
    """
    if modo_ambiente.upper() == "MOCK":
        return gerar_mock_domus()

    registros = buscar_json_domus_real()
    return pd.json_normalize(registros) if registros else pd.DataFrame()
