# Centralizador Diário de Relatórios — Vivo

Aplicação Web Local (Python + Flask) desenhada na arquitetura **"De Fora para Dentro"**:
- **Fora da Vivo (`ENV_MODE=MOCK`):** Simula as extrações dos 3 sistemas para construirmos e testarmos filtros, regras de negócio e o gerador de Excel sem precisar da intranet.
- **No Computador da Vivo (`ENV_MODE=PROD`):** Conecta na API do **DOMUS (P1)** e coleta as bases do **Anel Comutado (BI)** e **Backlog Diário (Maestro)**.
- **Zero bloqueio de bibliotecas:** Possui leitor e gerador nativos de arquivos `.xlsx` (OpenXML) em Python puro, funcionando mesmo se o proxy da Vivo bloquear a instalação do `openpyxl`.

---

## Estrutura das Abas (Na Tela e no Excel Gerado)

1. **`Resumo Geral`**:
   - Consolida a volumetria total e filtrada dos 3 relatórios.
   - Matriz cruzada por **Regional** (`P1 DOMUS x Anel Comutado x Backlog Maestro`).
   - Quebra automática por **Status / Severidade / Prioridade** de cada relatório.
2. **`P1 (DOMUS)`**:
   - Alimentado via **API REST (JSON)**.
   - Possui barra de filtros específica para as colunas do P1 (Regional, UF, Status, SLA, Causa Raiz, etc.).
3. **`Anel Comutado (BI)`**:
   - Alimentado via BI Intranet / Leitura automática da pasta `Downloads` ou Upload rápido.
   - Possui barra de filtros específica do Anel Comutado.
4. **`Backlog Diário (Maestro)`**:
   - Alimentado via Maestro / Leitura automática da pasta `Downloads` ou Upload rápido.
   - Possui barra de filtros específica do Maestro.

> 💡 **Inteligência Dinâmica de Filtros:** Assim que o seu script real da API do DOMUS rodar ou você carregar as planilhas reais do Anel Comutado e Maestro, o sistema **lê automaticamente os nomes das colunas reais** e monta os seletores de filtro na tela e o AutoFiltro no cabeçalho de cada aba do Excel!

---

## Como rodar (Aqui ou na Máquina da Vivo)

### 1. Instalar dependências (1ª vez)
```bash
pip install -r requirements.txt
```

### 2. Iniciar o sistema
Basta dar dois cliques em **`iniciar.bat`** (ou rodar no terminal):
```bash
python -m uvicorn app:app --port 8000 --reload
```
E abrir no navegador: **http://localhost:8000**

---

## Fluxo GitHub (Passando para o PC da Vivo)

1. **Onde colar o seu script da API do DOMUS:**
   - Abra o arquivo [`src/extractors/domus_api.py`](src/extractors/domus_api.py) e cole a lógica da sua requisição dentro da função `buscar_json_domus_real()`.
2. **Como configurar na máquina da Vivo sem vazar senhas no GitHub:**
   - No PC da Vivo, faça `git clone` / `git pull` do projeto.
   - Crie uma cópia do arquivo `.env.example` chamada **`.env`** (o arquivo `.env` é ignorado pelo Git).
   - Mude a primeira linha para `ENV_MODE=PROD` e preencha a URL/Token da API do DOMUS.
3. **Como funcionam o Anel Comutado (BI) e o Backlog Diário (Maestro) na Vivo:**
   - **Modo Pasta Downloads Automática (Zero configuração):** Basta você baixar a planilha no navegador da Vivo como já faz hoje e clicar em **"Atualizar Todas as Fontes"** no Centralizador — ele busca sozinho o arquivo mais recente na sua pasta `Downloads` do Windows!
   - **Modo Requisição Direta (1 Clique total):** No navegador da Vivo, aperte `F12` (aba *Network*) ao exportar a planilha do BI/Maestro, copie a URL e o `Cookie` para o seu `.env`, e o Python baixará direto sem precisar abrir a tela do BI.
