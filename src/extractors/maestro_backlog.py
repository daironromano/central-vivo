import os
from io import BytesIO
import pandas as pd
import requests
from src.extractors.anel_bi import buscar_arquivo_downloads_recente


def gerar_mock_backlog_maestro() -> pd.DataFrame:
    """
    Dados simulados do relatório Backlog Diário (Maestro) para desenvolvimento e testes.
    """
    dados = [
        {
            "ID_Ordem_Maestro": "MAE-2026-4410",
            "Fila": "Manutenção Rede Fibra",
            "Regional": "SP",
            "UF": "SP",
            "Prioridade": "P1 - Emergencial",
            "Status_Maestro": "Em Execução",
            "Aging_Dias": 1,
            "Faixa_Aging": "0 a 2 dias",
            "Equipe_Designada": "EPS Fibra Campinas",
            "Sistema_Origem": "Maestro",
        },
        {
            "ID_Ordem_Maestro": "MAE-2026-4398",
            "Fila": "Manutenção Energia",
            "Regional": "SUL",
            "UF": "PR",
            "Prioridade": "P1 - Emergencial",
            "Status_Maestro": "Aguardando Peça",
            "Aging_Dias": 4,
            "Faixa_Aging": "3 a 5 dias",
            "Equipe_Designada": "EPS Energia Sul",
            "Sistema_Origem": "Maestro",
        },
        {
            "ID_Ordem_Maestro": "MAE-2026-4102",
            "Fila": "Preventiva TX",
            "Regional": "NE",
            "UF": "PE",
            "Prioridade": "P2 - Alta",
            "Status_Maestro": "Backlog (Na Fila)",
            "Aging_Dias": 8,
            "Faixa_Aging": "Acima de 5 dias",
            "Equipe_Designada": "Engenharia Campo NE",
            "Sistema_Origem": "Maestro",
        },
        {
            "ID_Ordem_Maestro": "MAE-2026-4050",
            "Fila": "Manutenção Rede Fibra",
            "Regional": "RJ/ES",
            "UF": "RJ",
            "Prioridade": "P2 - Alta",
            "Status_Maestro": "Backlog (Na Fila)",
            "Aging_Dias": 6,
            "Faixa_Aging": "Acima de 5 dias",
            "Equipe_Designada": "EPS Rio Metro",
            "Sistema_Origem": "Maestro",
        },
        {
            "ID_Ordem_Maestro": "MAE-2026-4455",
            "Fila": "Core / Comutação",
            "Regional": "MG",
            "UF": "MG",
            "Prioridade": "P1 - Emergencial",
            "Status_Maestro": "Em Execução",
            "Aging_Dias": 0,
            "Faixa_Aging": "0 a 2 dias",
            "Equipe_Designada": "Equipe Core MG",
            "Sistema_Origem": "Maestro",
        },
        {
            "ID_Ordem_Maestro": "MAE-2026-4460",
            "Fila": "Manutenção Rede Fibra",
            "Regional": "SP",
            "UF": "SP",
            "Prioridade": "P3 - Normal",
            "Status_Maestro": "Backlog (Na Fila)",
            "Aging_Dias": 12,
            "Faixa_Aging": "Acima de 5 dias",
            "Equipe_Designada": "EPS Capital SP",
            "Sistema_Origem": "Maestro",
        },
    ]
    return pd.DataFrame(dados)


def extrair_backlog_maestro(modo_ambiente: str = "MOCK") -> pd.DataFrame:
    """
    Executa a extração do Backlog Diário (Maestro).
    """
    if modo_ambiente.upper() == "MOCK":
        return gerar_mock_backlog_maestro()

    url = os.getenv("MAESTRO_URL", "").strip()
    cookie = os.getenv("MAESTRO_COOKIE", "").strip()

    if url and cookie:
        headers = {"Cookie": cookie, "User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=60)
        resp.raise_for_status()
        try:
            return pd.read_excel(BytesIO(resp.content))
        except Exception:
            return pd.read_csv(BytesIO(resp.content), sep=";")

    padrao = os.getenv("MAESTRO_FILENAME_PATTERN", "backlog")
    return buscar_arquivo_downloads_recente(padrao)
