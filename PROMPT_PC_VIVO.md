# 📋 PROMPT PARA COPIAR E COLAR NO MODELO DO PC DA VIVO

> **Como usar:** Quando estiver no seu computador da Vivo, abra este arquivo no GitHub (`https://github.com/daironromano/central-vivo/blob/main/PROMPT_PC_VIVO.md`), copie o bloco abaixo e cole no chat da IA que você utiliza lá.

---

```markdown
Olá! Estamos desenvolvendo o projeto "Centralizador Diário de Relatórios — Vivo" em conjunto com outro agente de IA (Antigravity, que roda no meu computador pessoal fora da rede da Vivo). Nós sincronizamos nosso código e nossa memória através do repositório GitHub: https://github.com/daironromano/central-vivo

Dentro da pasta do projeto existe um arquivo chamado `MEMORIA_AGENTES.md` (e diretrizes em `GEMINI.md` e `.agents/skills/vivo-monochrome-icons/SKILL.md`).

Siga rigorosamente este protocolo de trabalho comigo:

1. LEITURA DE MEMÓRIA:
   - Se você tiver acesso aos arquivos locais da pasta `central-vivo`, leia imediatamente os arquivos `MEMORIA_AGENTES.md`, `app.py` e `src/extractors/domus_api.py`. (Se você for um chat no navegador sem acesso direto à pasta, me peça para colar o conteúdo de `MEMORIA_AGENTES.md` e `src/extractors/domus_api.py`).
   - Leia a última mensagem deixada pelo Agente Externo (`[Mensagem #001]`) em `MEMORIA_AGENTES.md`.

2. REGRAS OBRIGATÓRIAS DO PROJETO:
   - SEGURANÇA CORPORATIVA: Nunca coloque URLs internas reais com tokens, senhas, cookies ou dados sensíveis de clientes diretamente no código que vai para o GitHub nem no `MEMORIA_AGENTES.md`. Toda credencial/URL sensível deve ficar apenas no meu arquivo local `.env` (com `ENV_MODE=PROD`).
   - PADRÃO VISUAL: É proibido usar emojis coloridos ou ícones multicoloridos no HTML/UI. Todos os ícones devem ser SVGs em silhueta monocromática na cor Roxo Vivo (`#660099`).
   - ZERO DEPENDÊNCIAS BLOQUEADAS: O projeto usa Flask + leitor/escritor `.xlsx` nativos em Python puro (`src/core/excel_io.py` e `src/core/excel_builder.py`) para não depender de `openpyxl` se o proxy bloquear.

3. NOSSA MISSÃO AGORA NO PC DA VIVO:
   - Integrar meu script Python real da API do sistema DOMUS (relatório P1) dentro de `buscar_json_domus_real()` em `src/extractors/domus_api.py`.
   - Mapear as colunas reais e filtros dos 3 relatórios:
     1) P1 (DOMUS) — via API JSON
     2) Anel Comutado (BI) — via planilha/portal BI
     3) Backlog Diário (Maestro) — via planilha/sistema Maestro
   - Atualizar os nomes das colunas reais nos geradores de Mock (`gerar_mock_domus`, `gerar_mock_anel_comutado`, `gerar_mock_backlog_maestro`) com dados fictícios e em `colunas_filtro_sugeridas` no `app.py`, para que o Agente Externo (Antigravity) conheça a estrutura exata das nossas tabelas!

4. ATUALIZAÇÃO DE MEMÓRIA (SEMPRE AO FINAL):
   - Sempre que concluirmos uma etapa, gere a atualização da seção `[Mensagem #002]` no arquivo `MEMORIA_AGENTES.md` explicando para o Agente Externo (Antigravity) tudo o que fizemos, quais são as colunas reais descobertas em cada relatório e o que ele deve construir ou refinar a seguir.

Confirme que entendeu o protocolo e me diga o que precisa que eu te envie primeiro (meu script da API do DOMUS ou os cabeçalhos das planilhas).
```
