import os
import glob
from pathlib import Path
import pandas as pd
import requests
from src.core.excel_io import ler_xlsx_nativo


def buscar_arquivo_downloads_recente(padrao_nome: str) -> pd.DataFrame:
    """
    Procura na pasta Downloads do Windows o arquivo mais recente que contenha o padrão
    (ex: 'anel_comutado') caso você tenha baixado com 1 clique no navegador da Vivo,
    ou busca diretamente via requisição se ANEL_BI_URL estiver configurado com Cookie.
    """
    pasta_downloads = Path.home() / "Downloads"
    arquivos = []
    for ext in ["*.xlsx", "*.xls", "*.csv"]:
        for arq in glob.glob(str(pasta_downloads / ext)):
            if padrao_nome.lower() in os.path.basename(arq).lower():
                arquivos.append(arq)

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo contendo '{padrao_nome}' encontrado em {pasta_downloads}. "
            "Você também pode arrastar a planilha direto na tela do sistema!"
        )

    arquivo_mais_recente = max(arquivos, key=os.path.getmtime)
    if arquivo_mais_recente.lower().endswith(".csv"):
        try:
            return pd.read_csv(arquivo_mais_recente, sep=";", encoding="utf-8")
        except Exception:
            return pd.read_csv(arquivo_mais_recente, sep=",", encoding="latin1")
    return ler_xlsx_nativo(arquivo_mais_recente)


def gerar_mock_anel_comutado() -> pd.DataFrame:
    """
    Dados simulados do relatório Anel Comutado para desenvolvimento e testes.
    """
    dados = [
        {
            "ID_Anel": "ANEL-SPO-METRO-01",
            "Regional": "SP",
            "UF": "SP",
            "Tecnologia": "DWDM / OTN",
            "Status_Anel": "Aberto (Alarme)",
            "Severidade": "Crítica",
            "Trecho_Afetado": "SPO-CONSOLACAO <-> SPO- LAPA",
            "Capacidade_Gbps": 100,
            "Ocupacao_Pct": 84.5,
            "Tempo_Aberto_Horas": 4.2,
            "Ticket_Associado": "DOM-90811",
        },
        {
            "ID_Anel": "ANEL-CWB-SUL-04",
            "Regional": "SUL",
            "UF": "PR",
            "Tecnologia": "MPLS / IP",
            "Status_Anel": "Aberto (Alarme)",
            "Severidade": "Alta",
            "Trecho_Afetado": "CWB-CENTRO <-> CWB-PORTAO",
            "Capacidade_Gbps": 40,
            "Ocupacao_Pct": 72.0,
            "Tempo_Aberto_Horas": 6.5,
            "Ticket_Associado": "DOM-90815",
        },
        {
            "ID_Anel": "ANEL-RJO-COSTA-02",
            "Regional": "RJ/ES",
            "UF": "RJ",
            "Tecnologia": "DWDM / OTN",
            "Status_Anel": "Normalizado",
            "Severidade": "Normal",
            "Trecho_Afetado": "Sem falha",
            "Capacidade_Gbps": 200,
            "Ocupacao_Pct": 61.2,
            "Tempo_Aberto_Horas": 0.0,
            "Ticket_Associado": "DOM-90830",
        },
        {
            "ID_Anel": "ANEL-REC-NE-09",
            "Regional": "NE",
            "UF": "PE",
            "Tecnologia": "SDH / Metro",
            "Status_Anel": "Degradado",
            "Severidade": "Média",
            "Trecho_Afetado": "REC-BOA_VIAGEM <-> REC- CENTRO",
            "Capacidade_Gbps": 10,
            "Ocupacao_Pct": 91.0,
            "Tempo_Aberto_Horas": 2.1,
            "Ticket_Associado": "DOM-90822",
        },
        {
            "ID_Anel": "ANEL-CPS-INTERIOR-07",
            "Regional": "SP",
            "UF": "SP",
            "Tecnologia": "DWDM / OTN",
            "Status_Anel": "Aberto (Alarme)",
            "Severidade": "Crítica",
            "Trecho_Afetado": "CPS-CENTRO <-> JUNDIAI-01",
            "Capacidade_Gbps": 100,
            "Ocupacao_Pct": 88.9,
            "Tempo_Aberto_Horas": 7.8,
            "Ticket_Associado": "DOM-90841",
        },
    ]
    return pd.DataFrame(dados)


def extrair_anel_comutado(modo_ambiente: str = "MOCK") -> pd.DataFrame:
    """
    Executa a extração do Anel Comutado.
    """
    if modo_ambiente.upper() == "MOCK":
        return gerar_mock_anel_comutado()

    url = os.getenv("ANEL_BI_URL", "").strip()
    cookie = os.getenv("ANEL_BI_COOKIE", "").strip()

    # Se tiver URL direta + Cookie de sessão da Intranet configurado, baixa direto via HTTP:
    if url and cookie:
        headers = {"Cookie": cookie, "User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=60)
        resp.raise_for_status()
        from io import BytesIO
        try:
            return pd.read_excel(BytesIO(resp.content))
        except Exception:
            return pd.read_csv(BytesIO(resp.content), sep=";")

    # Caso contrário, busca automaticamente o último arquivo na pasta Downloads do PC da Vivo:
    padrao = os.getenv("ANEL_FILENAME_PATTERN", "anel")
    return buscar_arquivo_downloads_recente(padrao)
