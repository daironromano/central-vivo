---
name: vivo-clean-objective-ui
description: Enforces a strict clean, minimal, and objective UI standard for Vivo dashboards and web platforms: zero subtitles under titles, zero unnecessary parenthetical explanations, no technical metadata (origin/IPs, execution mode, background job badges, security algorithm names, audit trails), read-only tables on the web (filling happens only in exported Excel sheets), no manual file upload buttons when automated sync exists, last update timestamp in the top-right corner, user management opened by clicking the user button (not as a tab), and clickable brand logo/title returning to the home view.
---

# Vivo Clean & Objective UI Standard (`vivo-clean-objective-ui`)

Sempre que criar ou editar interfaces HTML, CSS ou JavaScript para plataformas e dashboards da Vivo, aplique rigorosamente estas diretrizes de **Interface Limpa e Objetiva (Menos Informação, Mais Objetividade)**:

## 1. Zero Subtítulos e Zero Parênteses Desnecessários
- **Proibido usar subtítulos explicativos** abaixo do título principal da plataforma ou dentro de cabeçalhos de cartões.
- **Proibido usar parênteses explicativos** em botões, abas, títulos de seções ou rótulos de formulários:
  - **Correto:** `Baixar Excel`, `Resumo Executivo`, `P1`, `AnelComutado`, `CellDowntime`, `Matriz Consolidada por UF`, `Detalhamento Operacional`, `Perfis e Usuários`, `Filtros`, `Senha`.
  - **Proibido:** `Baixar Excel (.xlsx)`, `Resumo Geral (Exclusivo Online)`, `P1 (DOMUS)`, `AnelComutado (BI)`, `CellDowntime (ENM CLI 2º Plano)`, `Gestão de Perfis (RBAC — Argon2id)`, `Nova Senha (mín. 6 caract.)`.

## 2. Ocultar Metadados Técnicos na Interface
- **Não exibir** crachás de modo de execução (`MODO LOCAL` / `MODO PRODUÇÃO`).
- **Não exibir** crachás ou caixas técnicas de execução em segundo plano (`ENM 2º PLANO`, comandos CLI ou IPs de API como `Origem: API DOMUS (10.215.39.118:8001)`). Processos em segundo plano devem rodar de forma transparente.
- **Não exibir** tabelas de Trilha de Auditoria na interface do usuário.

## 3. Posicionamento e Navegação Padronizados
- **Logo e Nome da Plataforma Clicáveis:** O ícone e o título principal na barra superior devem ser clicáveis e retornar imediatamente para a página inicial (`Resumo Executivo`).
- **Data e Hora da Última Atualização:** Exibir apenas `Última atualização: DD/MM/AAAA HH:MM:SS` alinhado no **canto superior direito**.
- **Perfis e Segurança no Botão do Usuário:** A gestão de usuários e perfis nunca deve ocupar uma aba de navegação principal; deve abrir em modal/painel ao clicar diretamente sobre o botão do usuário logado na barra superior.

## 4. Tabelas Somente Leitura e Sincronização Direta
- **Sem Campos de Preenchimento na Web:** Não colocar `<input>` de edição dentro das células das tabelas web quando o preenchimento operacional for feito na planilha Excel exportada.
- **Sem Botão de Importar Base Manual:** Quando os dados são sincronizados dos sistemas oficiais pelo botão `Sincronizar`, não exibir botões de upload manual de arquivos.

## 5. Tela de Login Enxuta
- Exibir apenas o formulário direto de **Login** (`Usuário` e `Senha`) sem abas superiores poluídas e sem expor senhas na tela, mantendo apenas links discretos no rodapé do card (`Criar usuário` e `Recuperar senha`).
