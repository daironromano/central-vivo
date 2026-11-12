import os
import glob
from pathlib import Path
import pandas as pd
from src.core.excel_io import ler_xlsx_nativo, converter_serial_excel_para_data

COLUNAS_FORMATADAS_ANEL = [
    "Sequencia",
    "SequenciaRaiz",
    "RAIZ",
    "Prioridade",
    "Aging",
    "Categoria",
    "Classificação",
    "Grupo Responsável",
    "GRUPO_PLANTA_INTERNA",
    "Localidade",
    "Gestor Atual",
    "UF",
    "SiglaLocalidade",
    "Sigla Site",
    "DataCriacao",
    "DataApresentacao",
    "Técnico",
    "Data",
    "Observação",
    "Alarme",
]


def baixar_anel_via_playwright() -> str:
    """
    Executa automação via Playwright no computador da Vivo para acessar o BI de Anel Comutado,
    aproveitando a sessão autenticada (SSO) do navegador corporativo (Edge/Chrome),
    e baixa a planilha .xlsx para a pasta temporária/Downloads.
    """
    url_bi = os.getenv("ANEL_BI_URL", "").strip()
    if not url_bi:
        raise ValueError("Defina ANEL_BI_URL no arquivo .env para usar a extração Playwright.")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright não encontrado. No PC da Vivo, execute 'pip install playwright' "
            "ou baixe a planilha no navegador que o sistema puxa automático da pasta Downloads!"
        ) from exc

    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pasta_destino = os.path.join(raiz, "downloads_temp")
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, "anel_playwright_export.xlsx")

    canal_navegador = os.getenv("PLAYWRIGHT_BROWSER_CHANNEL", "msedge")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "False").lower() == "true"
    seletor_export = os.getenv(
        "ANEL_PLAYWRIGHT_EXPORT_SELECTOR",
        "button:has-text('Exportar'), button[title*='Export'], [aria-label*='Exportar']",
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=canal_navegador, headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(url_bi, wait_until="networkidle", timeout=90000)

        with page.expect_download(timeout=60000) as download_info:
            page.locator(seletor_export).first.click()

        download = download_info.value
        download.save_as(caminho_arquivo)
        browser.close()

    return caminho_arquivo


def carregar_anel_bruto_local() -> pd.DataFrame:
    """
    Lê a planilha bruta (bruto/anel.xlsx) ou formatada (formatado/anel.xlsx) do projeto.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    caminho_bruto = os.path.join(raiz, "bruto", "anel.xlsx")
    caminho_fmt = os.path.join(raiz, "formatado", "anel.xlsx")

    if os.path.exists(caminho_bruto):
        return ler_xlsx_nativo(caminho_bruto)
    if os.path.exists(caminho_fmt):
        return ler_xlsx_nativo(caminho_fmt)
    return pd.DataFrame(columns=COLUNAS_FORMATADAS_ANEL)


def formatar_anel_comutado(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o DataFrame bruto do Power BI (34 colunas de bruto/anel.xlsx)
    exatamente nas 20 colunas oficiais de formatado/anel.xlsx (Aba 'Export'):
    ['Sequencia', 'SequenciaRaiz', 'RAIZ', 'Prioridade', 'Aging', 'Categoria',
     'Classificação', 'Grupo Responsável', 'GRUPO_PLANTA_INTERNA', 'Localidade',
     'Gestor Atual', 'UF', 'SiglaLocalidade', 'Sigla Site', 'DataCriacao',
     'DataApresentacao', 'Técnico', 'Data', 'Observação', 'Alarme']
    """
    if df_bruto is None or df_bruto.empty:
        return pd.DataFrame(columns=COLUNAS_FORMATADAS_ANEL)

    df = df_bruto.copy()
    mapa_lower = {c.lower().strip(): c for c in df.columns}

    saida = pd.DataFrame()
    for col_alvo in COLUNAS_FORMATADAS_ANEL:
        col_origem = mapa_lower.get(col_alvo.lower())
        if col_origem and col_origem in df.columns:
            saida[col_alvo] = df[col_origem].fillna("").astype(str)
        else:
            saida[col_alvo] = ""

    # Converte números seriais de data do Excel para formato legível DD/MM/YYYY HH:MM
    for col_dt in ("DataCriacao", "DataApresentacao", "Data"):
        if col_dt in saida.columns:
            saida[col_dt] = saida[col_dt].apply(converter_serial_excel_para_data)

    # Remove linhas inválidas onde Sequencia seja texto de rodapé de filtros do Power BI
    if "Sequencia" in saida.columns:
        saida = saida[~saida["Sequencia"].str.lower().str.startswith("filtros aplicados")].reset_index(drop=True)

    return saida


def extrair_anel_comutado(modo_ambiente: str = "MOCK") -> pd.DataFrame:
    """
    Executa a extração do Anel Comutado (via Playwright ou pasta Downloads em PROD,
    ou lendo bruto/anel.xlsx em MOCK) e retorna no formato exato de formatado/anel.xlsx.
    """
    if modo_ambiente.upper() == "PROD":
        # 1. Tenta via Playwright se ANEL_BI_URL estiver configurado
        if os.getenv("ANEL_BI_URL", "").strip():
            try:
                arq_pw = baixar_anel_via_playwright()
                return formatar_anel_comutado(ler_xlsx_nativo(arq_pw))
            except Exception:
                pass

        # 2. Procura na pasta Downloads do Windows o arquivo mais recente do Anel Comutado
        padrao = os.getenv("ANEL_FILENAME_PATTERN", "anel")
        pasta_downloads = Path.home() / "Downloads"
        candidatos = []
        for ext in ("*.xlsx", "*.xls", "*.csv"):
            for arq in glob.glob(str(pasta_downloads / ext)):
                if padrao.lower() in os.path.basename(arq).lower():
                    candidatos.append(arq)
        if candidatos:
            mais_recente = max(candidatos, key=os.path.getmtime)
            df_dl = ler_xlsx_nativo(mais_recente)
            return formatar_anel_comutado(df_dl)

    df_local = carregar_anel_bruto_local()
    return formatar_anel_comutado(df_local)
