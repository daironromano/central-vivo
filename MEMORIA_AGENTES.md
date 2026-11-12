# MEMÓRIA COMPARTILHADA ENTRE AGENTES (CASA <-> TRABALHO VIVO)

> **Propósito deste arquivo:** Servir como ponte de memória contínua e canal de comunicação assíncrona via GitHub entre:
> - **Agente Externo (Antigravity - PC Pessoal):** Constrói a arquitetura MVC (`backend/` e `frontend/`), segurança RBAC, transformadores Bruto->Formatado e automações (`ENV_MODE=MOCK`).
> - **Agente Interno (IA no PC da Vivo):** Executa e ajusta na intranet da Vivo (`ENV_MODE=PROD`).

---

## REGRAS DE OURO DE SEGURANÇA E UI (OBRIGATÓRIO PARA AMBOS OS AGENTES)
1. **NUNCA** escreva tokens reais, senhas, cookies de sessão ou credenciais diretamente no código que vai para o GitHub nem neste arquivo.
2. Credenciais e senhas da API do DOMUS (`10.215.39.118:8001`) e do ENM devem ficar **exclusivamente** no arquivo local `.env` (ignorado pelo `.gitignore`).
3. **Regra Visual (`vivo-monochrome-icons`):** Zero emojis coloridos. Todos os ícones são SVGs monocromáticos em silhueta na cor **Roxo Vivo (`#660099`)**.
4. **Regra de Interface Limpa e Objetiva (`vivo-clean-objective-ui`):** Menos informação e mais objetividade sempre — sem subtítulos, sem parênteses desnecessários (`Baixar Excel`, `Resumo Executivo`, `P1`, `AnelComutado`, `CellDowntime`), sem exibir modo de execução/origem/IP/trilha de auditoria, tabelas web somente leitura (preenchimento apenas no Excel baixado), data/hora da última atualização no canto superior direito, gestão de usuários ao clicar no botão do usuário e logo/nome clicável voltando ao início.

---

## ARQUITETURA MVC SEPARADA (`backend/` & `frontend/`)

```
vivo-centralizador/
├── app.py                             # Entrypoint raiz que inicializa `criar_app()` de `backend/app.py`
├── backend/                           # CAMADA BACKEND (Models, Controllers, Extractors, Core)
│   ├── app.py                         # Factory Flask conectando `backend/` às Views e Assets de `frontend/`
│   ├── models/                        # CAMADA MODEL
│   │   ├── user_model.py              # Perfis RBAC ('administrador' e 'usuario'), Auto-Cadastro e Recuperação de Senha (Argon2id)
│   │   └── report_model.py            # Gestão dos 3 relatórios ('P1', 'AnelComutado', 'CellDowntime') + Worker ENM em 2º plano
│   ├── controllers/                   # CAMADA CONTROLLER
│   │   ├── auth_controller.py         # Login, Registro (/api/auth/register), Recuperação (/api/auth/recover), Sessão HMAC-SHA256
│   │   └── report_controller.py       # Extração, status do ENM em 2º plano (/api/enm-cli/status) e exportação .xlsx (sem Resumo)
│   ├── extractors/                    # CONECTORES E FORMATADORES OFICIAIS
│   │   ├── domus_api.py               # POST /auth/login -> x-access-token -> GET /query/calamidade-details -> Planilha 'P1'
│   │   ├── anel_playwright.py         # Playwright BI -> Limpeza de cabeçalho Power BI -> Planilha 'AnelComutado'
│   │   └── enm_cli.py                 # Ericsson ENM CLI em 2º Plano (Thread Daemon: P1, 4G_5G, 3G) + PROCV -> Planilha 'CellDowntime'
│   └── core/
│       ├── security.py                # Motor de Segurança (Argon2id, HMAC-SHA256, CSRF, Lockout 5 tentativas, Audit Log)
│       ├── excel_io.py                # Leitor OpenXML (.xlsx/.xlsm) com suporte a células posicionais Power BI e datas seriais
│       └── excel_builder.py           # Gerador OpenXML (.xlsx) exportando EXCLUSIVAMENTE as 3 abas: P1, AnelComutado, CellDowntime
└── frontend/                          # CAMADA FRONTEND (Views HTML e Assets Estáticos)
    ├── views/
    │   ├── login.html                 # Tela de Autenticação limpa (Sem senhas expostas + Abas Entrar, Criar Usuário e Recuperar Senha)
    │   └── dashboard.html             # Painel Web com Resumo Geral (Exclusivo Online) + Abas P1, AnelComutado, CellDowntime e Admin
    └── assets/
        ├── css/style.css              # Estilos corporativos Vivo + ícones monocromáticos #660099
        └── js/app.js                  # Controller Frontend + Monitoramento em tempo real do Worker ENM em 2º Plano
```

---

## DIÁRIO DE SINCRONIZAÇÃO (LOG DE MENSAGENS ENTRE OS MODELOS)

### [Mensagem #004] — De: Agente Externo (Antigravity) -> Para: Agente Interno (PC da Vivo)
**Status:** Refatoração `backend/` + `frontend/` concluída, Excel consolidado ajustado, Login com Cadastro/Recuperação de Senha e Comandos ENM rodando em 2º plano!
**Resumo das atualizações solicitadas pelo Dairon:**

1. **Planilha Consolidada Exportada (`.xlsx`) — Sem Resumo e Nomes Padronizados (`backend/core/excel_builder.py`):**
   - A aba `Resumo Geral` permanece **exclusivamente na plataforma online** (`frontend/views/dashboard.html`).
   - O arquivo `.xlsx` baixado contém **apenas as 3 planilhas dos relatórios diários**, nomeadas exatamente como:
     - `P1` (antigo `portal_calamidade_tickets_total`)
     - `AnelComutado` (antigo `Export`)
     - `CellDowntime` (antigo `Consolidado_CellDowntime`)
2. **Separação Física `backend/` e `frontend/` (MVC Completo):**
   - Todo o código servidor (`models/`, `controllers/`, `extractors/`, `core/`) foi organizado dentro de `backend/`.
   - Todos os templates HTML (`views/login.html`, `views/dashboard.html`) e recursos estáticos (`assets/css/style.css`, `assets/js/app.js`) foram organizados dentro de `frontend/`.
3. **Tela de Login Limpa + Criar Usuário + Recuperar Senha (`frontend/views/login.html`):**
   - Removidas todas as senhas e dicas de credenciais da frente da tela de login.
   - Adicionadas as abas **"Criar Usuário"** (`POST /api/auth/register` com palavra de segurança criptografada com Argon2id) e **"Recuperar Senha"** (`POST /api/auth/recover` validando a palavra de segurança para redefinir a senha).
4. **Execução Automática em 2º Plano dos Comandos CLI no Ericsson ENM (`backend/extractors/enm_cli.py`):**
   - Ao entrar na plataforma (`GET /`) ou sincronizar (`POST /api/extract-all`), o backend dispara automaticamente uma thread `daemon=True` (`disparar_worker_enm_segundo_plano()`) que executa em segundo plano os 3 comandos CLI (`P1`, `4G_5G`, `3G`) no ENM (`enmscripting` / REST API em `PROD`, ou leitura de `Celldowntime_PA_AP.xlsm` em `MOCK`) e aplica o `PROCV` (`VLOOKUP`) automático contra `grid_4g_5g` e `grid_3g`.
   - O frontend acompanha o progresso em tempo real via `/api/enm-cli/status`.
