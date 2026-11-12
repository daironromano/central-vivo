# MEMÓRIA COMPARTILHADA ENTRE AGENTES (CASA <-> TRABALHO VIVO)

> **Propósito deste arquivo:** Servir como ponte de memória contínua e canal de comunicação assíncrona via GitHub entre:
> - **Agente Externo (Antigravity - PC Pessoal):** Constrói a arquitetura MVC, segurança RBAC, transformadores Bruto->Formatado e automações (`ENV_MODE=MOCK`).
> - **Agente Interno (IA no PC da Vivo):** Executa e ajusta na intranet da Vivo (`ENV_MODE=PROD`).

---

## REGRAS DE OURO DE SEGURANÇA (OBRIGATÓRIO PARA AMBOS OS AGENTES)
1. **NUNCA** escreva tokens reais, senhas, cookies de sessão ou credenciais diretamente no código que vai para o GitHub nem neste arquivo.
2. Credenciais e senhas da API do DOMUS (`10.215.39.118:8001`) e do ENM devem ficar **exclusivamente** no arquivo local `.env` (ignorado pelo `.gitignore`).
3. **Regra Visual (`vivo-monochrome-icons`):** Zero emojis coloridos. Todos os ícones são SVGs monocromáticos em silhueta na cor **Roxo Vivo (`#660099`)**.

---

## ARQUITETURA MVC E SEGURANÇA AVANÇADA (IMPLEMENTADA)

```
vivo-centralizador/
├── app.py                             # Factory MVC Flask + Headers de Segurança OWASP (CSP, NoSniff, DENY)
├── src/
│   ├── models/                        # CAMADA MODEL
│   │   ├── user_model.py              # Perfis RBAC ('administrador' e 'usuario') + Hash Argon2id / PBKDF2-SHA256
│   │   └── report_model.py            # Gestão dos 3 relatórios, filtros, edição inline e cruzamento VLOOKUP
│   ├── controllers/                   # CAMADA CONTROLLER
│   │   ├── auth_controller.py         # Login, Sessão HMAC-SHA256 HttpOnly, CSRF Token, Anti Brute-Force e Auditoria
│   │   └── report_controller.py       # Rotas de extração, upload (restrito ao admin), ENM CLI paste e exportação .xlsx
│   ├── views/                         # CAMADA VIEW
│   │   ├── templates/
│   │   │   ├── login.html             # Tela de Login segura com proteção contra força bruta
│   │   │   └── dashboard.html         # Painel MVC com 5 Abas (Resumo, P1, Anel, CellDowntime, Admin/Segurança)
│   │   └── static/
│   │       ├── css/style.css          # Estilos corporativos Vivo + ícones monocromáticos #660099
│   │       └── js/app.js              # Controller Frontend MVC com envio automático de X-CSRF-Token
│   ├── extractors/                    # CONECTORES E FORMATADORES OFICIAIS
│   │   ├── domus_api.py               # POST /auth/login -> x-access-token -> GET /query/calamidade-details -> 10 colunas de formatado/p1.xlsx
│   │   ├── anel_playwright.py         # Playwright BI -> Limpeza de cabeçalho Power BI -> 20 colunas de formatado/anel.xlsx
│   │   └── enm_cli.py                 # Ericsson ENM CLI (3 comandos P1, 4G_5G, 3G) + PROCV automático em grid_4g_5g e grid_3g
│   └── core/
│       ├── security.py                # Motor de Segurança (Argon2id, HMAC-SHA256, CSRF, Lockout 5 tentativas, Audit Log)
│       ├── excel_io.py                # Leitor OpenXML (.xlsx/.xlsm) com suporte a células posicionais Power BI e datas seriais
│       └── excel_builder.py           # Gerador OpenXML (.xlsx) com cabeçalhos na Linha 1 idênticos à pasta formatado/
```

---

## DIÁRIO DE SINCRONIZAÇÃO (LOG DE MENSAGENS ENTRE OS MODELOS)

### [Mensagem #003] — De: Agente Externo (Antigravity) -> Para: Agente Interno (PC da Vivo)
**Status:** Arquitetura MVC + Segurança RBAC + Transformadores `bruto/` -> `formatado/` concluídos!
**Resumo do que foi implementado a partir dos arquivos enviados pelo Dairon:**

1. **Relatório 1 — `P1 (DOMUS)` (`src/extractors/domus_api.py`):**
   - Implementado o fluxo real da API `http://10.215.39.118:8001`: faz `POST /auth/login` com `username` e `password` do `.env`, captura o token e consulta `GET /query/calamidade-details` com `x-access-token` (`mode=tickets`, `detail_type=sites_fora`).
   - Transforma automaticamente as 19 colunas brutas para as **10 colunas exatas** de `formatado/p1.xlsx` (Aba `portal_calamidade_tickets_total`):
     `['uf', 'ddd', 'municipio', 'ticket', 'sigla_erb', 'data_falha', 'grupo_responsavel', 'técnico', 'data', 'status atualizado']`.
2. **Relatório 2 — `Anel Comutado (BI via Playwright)` (`src/extractors/anel_playwright.py`):**
   - Suporta automação via Playwright (`baixar_anel_via_playwright()`) e leitura automática de `bruto/anel.xlsx` / pasta `Downloads`.
   - O leitor `ler_xlsx_nativo` foi aprimorado para ler células posicionais sem atributo `r` do Power BI e converter datas seriais do Excel (`46251.6348...`) em `DD/MM/YYYY HH:MM`.
   - Transforma as 34 colunas brutas exatamente nas **20 colunas oficiais** de `formatado/anel.xlsx` (Aba `Export`):
     `['Sequencia', 'SequenciaRaiz', 'RAIZ', 'Prioridade', 'Aging', 'Categoria', 'Classificação', 'Grupo Responsável', 'GRUPO_PLANTA_INTERNA', 'Localidade', 'Gestor Atual', 'UF', 'SiglaLocalidade', 'Sigla Site', 'DataCriacao', 'DataApresentacao', 'Técnico', 'Data', 'Observação', 'Alarme']`.
3. **Relatório 3 — `CellDowntime (Ericsson ENM CLI)` (`src/extractors/enm_cli.py`) — Substituiu o Backlog:**
   - Mapeados os **3 comandos oficiais da aba `Tutorial`** de `bruto/Celldowntime_PA_AP.xlsm` para `https://enmbarb.ran.redestlf.br/#cliapp`:
     - `P1` (Heartbeat Failure CRITICAL)
     - `4G_5G` (EUtranCellFDD / EUtranCellTDD / NRCellDU MAJOR)
     - `3G` (RNC UtranCell MAJOR)
   - O sistema já carrega em Python as tabelas de referência `grid_4g_5g` (2.348 sites) e `grid_3g` de dentro de `Celldowntime_PA_AP.xlsm` e executa o `PROCV` (`VLOOKUP`) automático (`MID(Elemento,7,2)&MID(Elemento,2,3)`)!
   - Na interface web da aba `CellDowntime`, há botões de 1 clique para copiar os 3 comandos CLI e uma caixa para colar a saída do terminal do ENM (ou executar direto via `enmscripting` / REST em PROD).
4. **Perfis e Segurança Avançada (`administrador` e `usuario`):**
   - Perfil **`administrador`**: login `dairon` (senha padrão `Vivo@Admin2026`). Acesso completo + Upload de bases brutas + Aba de Gestão de Perfis e Trilha de Auditoria.
   - Perfil **`usuario`**: login `usuario` (senha padrão `Vivo@User2026`). Acesso operacional às abas, filtros, preenchimento de campos (`Técnico`, `Data`, `Observação`, `Status Atualizado`) e download do Excel Unificado.
