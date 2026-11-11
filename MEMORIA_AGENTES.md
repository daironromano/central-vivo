# MEMÓRIA COMPARTILHADA ENTRE AGENTES (CASA <-> TRABALHO VIVO)

> **Propósito deste arquivo:** Servir como ponte de memória contínua e canal de comunicação assíncrona via GitHub entre:
> - **Agente Externo (Antigravity - PC Pessoal):** Constrói a arquitetura, interface, gerador de Excel, filtros e melhorias estruturais (`ENV_MODE=MOCK`).
> - **Agente Interno (IA no PC da Vivo):** Tem acesso ao script real da API do DOMUS, às planilhas reais do Anel Comutado (BI) e Backlog Diário (Maestro), e ao ambiente de rede corporativa (`ENV_MODE=PROD`).

---

## REGRAS DE OURO DE SEGURANÇA (OBRIGATÓRIO PARA AMBOS OS AGENTES)
1. **NUNCA** escreva tokens reais, senhas, cookies de sessão, URLs sensíveis com credenciais ou dados reais de clientes neste arquivo ou no código-fonte.
2. Credenciais e URLs reais da Intranet devem ficar **exclusivamente** no arquivo local `.env` da máquina da Vivo (já bloqueado no `.gitignore`).
3. Para sincronizar a estrutura dos dados entre o PC da Vivo e o PC Pessoal, registre neste arquivo **apenas os nomes das colunas (schema), tipos de dados e regras de negócio/filtros**.

---

## RESUMO DA ARQUITETURA ATUAL (O QUE JÁ ESTÁ PRONTO)

* **Stack (Zero bloqueio de proxy):**
  * Backend em **Flask** (`app.py`) + `pandas` + `requests` + `python-dotenv`.
  * Leitor e Gerador de Excel `.xlsx` **100% nativos em Python puro (OpenXML)** em `src/core/excel_io.py` e `src/core/excel_builder.py` (funciona mesmo sem `openpyxl` instalado na máquina da Vivo).
  * Frontend em HTML/CSS/JS puro offline (`src/static/index.html`) — zero dependência de CDN externo.
* **Regra Visual Estrita (`vivo-monochrome-icons`):**
  * **PROIBIDO** usar emojis coloridos ou ícones multicoloridos.
  * Todos os ícones devem ser SVGs em silhueta monocromática na cor **Roxo Vivo (`#660099`)**.
* **4 Abas do Sistema (Na Web e no `.xlsx` exportado):**
  1. `Resumo Geral`: Consolida volumetria, matriz cruzada por Regional (`P1 DOMUS x Anel Comutado x Backlog Maestro`) e quebra por Status.
  2. `P1 (DOMUS)`: Extrator em `src/extractors/domus_api.py` (Via API JSON).
  3. `Anel Comutado (BI)`: Extrator em `src/extractors/anel_bi.py` (Via HTTP/Cookie ou leitura automática do arquivo mais recente na pasta `Downloads` ou Upload na tela).
  4. `Backlog Diário (Maestro)`: Extrator em `src/extractors/maestro_backlog.py` (Via HTTP/Cookie ou leitura automática da pasta `Downloads` ou Upload na tela).

---

## DIÁRIO DE SINCRONIZAÇÃO (LOG DE MENSAGENS ENTRE OS MODELOS)

### [Mensagem #001] — De: Agente Externo (Antigravity) -> Para: Agente Interno (PC da Vivo)
**Status:** Base 100% funcional enviada ao GitHub (`main`).
**O que você (Agente do PC da Vivo) deve fazer agora junto com o Dairon:**

1. **Configurar o ambiente local na Vivo:**
   - Criar o arquivo `.env` copiando de `.env.example` e definir `ENV_MODE=PROD`.
2. **Integrar o Script Real da API do DOMUS (`P1`):**
   - O Dairon já possui o script Python que consome a API do DOMUS e retorna um JSON.
   - Cole a lógica desse script dentro da função `buscar_json_domus_real()` no arquivo `src/extractors/domus_api.py`.
   - Verifique quais são as **colunas reais** retornadas pelo JSON e atualize a lista `colunas_filtro_sugeridas` de `"p1_domus"` no `app.py` (e atualize o `gerar_mock_domus()` com os nomes reais das colunas e dados fictícios para eu saber aqui fora como é a estrutura!).
3. **Mapear as Planilhas Reais do `Anel Comutado (BI)` e `Backlog Diário (Maestro)`:**
   - Peça ao Dairon uma amostra do cabeçalho (nomes das colunas) ou leia com Python as planilhas reais do **Anel Comutado** e do **Backlog Diário (Maestro)**.
   - Atualize `colunas_filtro_sugeridas` em `app.py` e os geradores `gerar_mock_anel_comutado()` e `gerar_mock_backlog_maestro()` com os nomes exatos das colunas reais.
   - Verifique com o Dairon quais filtros específicos cada aba deve ter e qual cálculo exato deve aparecer na aba `Resumo Geral`.
4. **Registrar a resposta abaixo (`[Mensagem #002]`):**
   - Antes do Dairon dar `git commit` e `git push` (ou me copiar o resumo), escreva abaixo na seção `[Mensagem #002]` o que foi alterado, quais são as colunas reais dos 3 relatórios e o que precisa que eu construa a seguir!

---

### [Mensagem #002] — De: Agente Interno (PC da Vivo) -> Para: Agente Externo (Antigravity)
*(Espaço reservado para o modelo do computador da Vivo preencher com os nomes reais das colunas, ajustes feitos na API do DOMUS e próximos passos)*
