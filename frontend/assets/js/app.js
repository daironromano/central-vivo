// Catálogo de Ícones em Silhueta Monocromática Roxo Vivo (#660099)
const ICONS = {
  sync: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74A7.93 7.93 0 004 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>`,
  download: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>`,
  search: `<svg class="icon-vivo" style="width:13px;height:13px;" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>`,
  sliders: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>`,
  alert: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>`,
  shield: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>`,
  user: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`,
  trash: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`,
  save: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>`
};

let ESTADO_ATUAL = {
  usuario: { username: "", nome: "", perfil: "usuario", csrf_token: "" },
  enm_background_job: {},
  relatorios: {}
};

let FILTROS_POR_ABA = {
  p1_domus: {},
  anel_comutado: {},
  celldowntime: {}
};

let BUSCA_POR_ABA = {
  p1_domus: "",
  anel_comutado: "",
  celldowntime: ""
};

let TIMER_ENM_POLL = null;

function headersSeguros(isJson = true) {
  const h = { "X-CSRF-Token": ESTADO_ATUAL.usuario.csrf_token || "" };
  if (isJson) h["Content-Type"] = "application/json";
  return h;
}

function mostrarNotificacao(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => { t.style.display = "none"; }, 3500);
}

function trocarAba(abaId) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

  const btn = document.getElementById(`tabbtn-${abaId}`);
  const panel = document.getElementById(`panel-${abaId}`);
  if (btn) btn.classList.add("active");
  if (panel) panel.classList.add("active");

  if (abaId === "resumo") {
    renderizarResumoGeral();
  }
}

function obterRegistrosFiltrados(repId) {
  const rep = ESTADO_ATUAL.relatorios[repId];
  if (!rep || !rep.registros) return [];
  const filtros = FILTROS_POR_ABA[repId] || {};
  const termo = (BUSCA_POR_ABA[repId] || "").trim().toLowerCase();

  return rep.registros.filter(row => {
    for (const [col, val] of Object.entries(filtros)) {
      if (val && val !== "TODOS" && String(row[col]) !== String(val)) {
        return false;
      }
    }
    if (termo) {
      const bate = Object.entries(row).some(([k, v]) =>
        k !== "_row_idx" && String(v).toLowerCase().includes(termo)
      );
      if (!bate) return false;
    }
    return true;
  });
}

function atualizarFiltro(repId, coluna, valor) {
  if (!FILTROS_POR_ABA[repId]) FILTROS_POR_ABA[repId] = {};
  FILTROS_POR_ABA[repId][coluna] = valor;
  atualizarTabelaAba(repId);
  renderizarResumoGeral();
}

function atualizarBusca(repId, valor) {
  BUSCA_POR_ABA[repId] = valor;
  atualizarTabelaAba(repId);
  renderizarResumoGeral();
}

function limparFiltrosAba(repId) {
  FILTROS_POR_ABA[repId] = {};
  BUSCA_POR_ABA[repId] = "";
  renderizarPainelRelatorio(repId);
  renderizarResumoGeral();
  mostrarNotificacao("Filtros limpos.");
}

function iniciarMonitoramentoEnmSegundoPlano() {
  if (TIMER_ENM_POLL) clearInterval(TIMER_ENM_POLL);
  TIMER_ENM_POLL = setInterval(async () => {
    try {
      const res = await fetch("/api/enm-cli/status");
      if (!res.ok) return;
      const data = await res.json();
      const estavaRodando = ESTADO_ATUAL.enm_background_job && ESTADO_ATUAL.enm_background_job.em_execucao;
      ESTADO_ATUAL.enm_background_job = data.job || {};

      if (estavaRodando && !ESTADO_ATUAL.enm_background_job.em_execucao) {
        clearInterval(TIMER_ENM_POLL);
        TIMER_ENM_POLL = null;
        await carregarEstadoInicial();
      } else if (!ESTADO_ATUAL.enm_background_job.em_execucao) {
        clearInterval(TIMER_ENM_POLL);
        TIMER_ENM_POLL = null;
      }
    } catch (e) {
      clearInterval(TIMER_ENM_POLL);
      TIMER_ENM_POLL = null;
    }
  }, 1500);
}

function renderizarPainelRelatorio(repId) {
  const rep = ESTADO_ATUAL.relatorios[repId];
  const container = document.getElementById(`panel-${repId}`);
  if (!rep || !container) return;

  const filtrosDisp = rep.filtros_disponiveis || {};
  const selecoesAtuais = FILTROS_POR_ABA[repId] || {};
  const buscaAtual = BUSCA_POR_ABA[repId] || "";

  let controlesFiltroHtml = `
    <div class="filter-group">
      <label>${ICONS.search} <span>Busca</span></label>
      <input type="text" placeholder="Pesquisar..." value="${buscaAtual}"
             oninput="atualizarBusca('${repId}', this.value)" />
    </div>
  `;

  for (const [col, valores] of Object.entries(filtrosDisp)) {
    const valorSelecionado = selecoesAtuais[col] || "TODOS";
    const optionsHtml = [`<option value="TODOS">Todos</option>`]
      .concat(valores.map(v => `<option value="${v}" ${v === valorSelecionado ? "selected" : ""}>${v}</option>`))
      .join("");

    controlesFiltroHtml += `
      <div class="filter-group">
        <label>${col}</label>
        <select onchange="atualizarFiltro('${repId}', '${col}', this.value)">
          ${optionsHtml}
        </select>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <div class="card-title">${rep.aba_excel}</div>
        <div class="card-header-right">
          <span class="last-update-card">Última atualização: ${rep.atualizado_em}</span>
          <button class="btn btn-vivo" onclick="extrairUnico('${repId}')">
            ${ICONS.sync}
            <span>Sincronizar</span>
          </button>
        </div>
      </div>

      ${rep.erro ? `<div style="background:#f5ebf9;color:#4a0070;border:1px solid #660099;padding:12px;border-radius:8px;margin-bottom:14px;font-size:13px;display:flex;align-items:center;gap:8px;">${ICONS.alert} <span>${rep.erro}</span></div>` : ""}

      <div class="filter-bar">
        <div class="filter-bar-header">
          <span style="display:flex;align-items:center;gap:8px;">
            ${ICONS.sliders}
            <span>Filtros</span>
          </span>
          <button class="btn btn-outline" style="padding:4px 10px; font-size:11px;" onclick="limparFiltrosAba('${repId}')">
            Limpar Filtros
          </button>
        </div>
        <div class="filter-controls">
          ${controlesFiltroHtml}
        </div>
      </div>

      <div id="table-container-${repId}" class="table-wrapper"></div>
    </div>
  `;

  atualizarTabelaAba(repId);
}

function formatarCelula(val) {
  const s = String(val ?? "");
  const lower = s.toLowerCase();
  if (lower === "p1" || lower.includes("crític") || lower === "+24h") {
    return `<span class="badge badge-crit">${s}</span>`;
  }
  if (lower === "4g_5g" || lower === "3g" || lower === "p3" || lower === "p4") {
    return `<span class="badge badge-warn">${s}</span>`;
  }
  return s;
}

function atualizarTabelaAba(repId) {
  const rep = ESTADO_ATUAL.relatorios[repId];
  if (!rep) return;

  const filtrados = obterRegistrosFiltrados(repId);
  const countEl = document.getElementById(`count-${repId}`);
  if (countEl) countEl.textContent = `${filtrados.length}`;

  const tableContainer = document.getElementById(`table-container-${repId}`);
  if (!tableContainer) return;

  if (filtrados.length === 0) {
    tableContainer.innerHTML = `<div style="padding:24px;text-align:center;color:var(--text-muted);">Nenhum registro encontrado.</div>`;
    return;
  }

  const cols = rep.colunas || [];
  const thead = `<thead><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr></thead>`;
  const tbody = `<tbody>${filtrados.map(row => `
    <tr>${cols.map(c => `<td title="${String(row[c] ?? "").replace(/"/g, '&quot;')}">${formatarCelula(row[c])}</td>`).join("")}</tr>
  `).join("")}</tbody>`;

  tableContainer.innerHTML = `<table>${thead}${tbody}</table>`;
}

function renderizarResumoGeral() {
  const reps = ESTADO_ATUAL.relatorios;
  const ids = Object.keys(reps);
  if (ids.length === 0) return;

  let totalFiltradoGeral = 0;
  let kpiHtml = "";

  ids.forEach(repId => {
    const r = reps[repId];
    const filtrados = obterRegistrosFiltrados(repId);
    totalFiltradoGeral += filtrados.length;

    kpiHtml += `
      <div class="kpi-card">
        <h3>${r.aba_excel}</h3>
        <div class="kpi-value">${filtrados.length}</div>
        <div class="kpi-meta">
          <span>Registros</span>
          <a href="javascript:void(0)" onclick="trocarAba('${repId}')" style="color:var(--vivo-purple);font-weight:600;text-decoration:none;">Abrir ${r.aba_excel} →</a>
        </div>
      </div>
    `;
  });

  kpiHtml = `
    <div class="kpi-card">
      <h3>Resumo Executivo</h3>
      <div class="kpi-value">${totalFiltradoGeral}</div>
      <div class="kpi-meta">
        <span>Total de registros</span>
      </div>
    </div>
  ` + kpiHtml;

  document.getElementById("kpiGrid").innerHTML = kpiHtml;

  // Matriz por UF
  const ufsSet = new Set();
  const mapaUf = {};

  ids.forEach(repId => {
    mapaUf[repId] = {};
    const filtrados = obterRegistrosFiltrados(repId);
    filtrados.forEach(row => {
      const colUf = Object.keys(row).find(k => k.toLowerCase() === "uf");
      if (colUf && row[colUf]) {
        const ufVal = String(row[colUf]).trim().toUpperCase();
        if (ufVal) {
          ufsSet.add(ufVal);
          mapaUf[repId][ufVal] = (mapaUf[repId][ufVal] || 0) + 1;
        }
      }
    });
  });

  const ufsOrdenadas = Array.from(ufsSet).sort();
  let tabelaRegHtml = `
    <table>
      <thead>
        <tr>
          <th>UF</th>
          ${ids.map(id => `<th>${reps[id].aba_excel}</th>`).join("")}
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
  `;

  ufsOrdenadas.forEach(uf => {
    let somaLinha = 0;
    const colsHtml = ids.map(id => {
      const qtd = mapaUf[id][uf] || 0;
      somaLinha += qtd;
      return `<td><strong>${qtd}</strong></td>`;
    }).join("");

    tabelaRegHtml += `
      <tr>
        <td><strong>${uf}</strong></td>
        ${colsHtml}
        <td style="background:var(--vivo-purple-light);font-weight:800;color:var(--vivo-purple);">${somaLinha}</td>
      </tr>
    `;
  });

  tabelaRegHtml += `</tbody></table>`;
  document.getElementById("tabelaRegionalResumo").innerHTML = tabelaRegHtml;

  // Detalhamento Operacional
  let statusHtml = "";
  ids.forEach(repId => {
    const r = reps[repId];
    const filtrados = obterRegistrosFiltrados(repId);
    const colChave = (r.colunas || []).find(c =>
      ["grupo_responsavel", "prioridade", "fonte", "gestor atual"].includes(c.toLowerCase())
    );
    if (colChave) {
      const contagem = {};
      filtrados.forEach(row => {
        const val = row[colChave] || "N/I";
        contagem[val] = (contagem[val] || 0) + 1;
      });

      const linhasOrdenadas = Object.entries(contagem)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([st, qtd]) => `
          <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed #e5e7eb;font-size:12.5px;">
            <span>${st}</span>
            <strong style="color:var(--vivo-purple);">${qtd}</strong>
          </div>
        `).join("");

      statusHtml += `
        <div style="margin-bottom:16px;">
          <div style="font-size:12px;font-weight:700;color:var(--vivo-purple);text-transform:uppercase;margin-bottom:4px;">
            ${r.aba_excel}
          </div>
          ${linhasOrdenadas || "<small style='color:var(--text-muted)'>Sem registros</small>"}
        </div>
      `;
    }
  });

  document.getElementById("statusBreakdownResumo").innerHTML = statusHtml;
}

async function carregarEstadoInicial() {
  const res = await fetch("/api/state");
  if (res.status === 401) {
    window.location.href = "/login";
    return;
  }
  ESTADO_ATUAL = await res.json();
  atualizarInterfaceCompleta();
  if (ESTADO_ATUAL.enm_background_job && ESTADO_ATUAL.enm_background_job.em_execucao) {
    iniciarMonitoramentoEnmSegundoPlano();
  }
}

function atualizarInterfaceCompleta() {
  const u = ESTADO_ATUAL.usuario || {};
  const userBadge = document.getElementById("userBadge");
  userBadge.innerHTML = `${u.perfil === "administrador" ? ICONS.shield : ICONS.user} <span>${u.nome}</span>`;

  // Data e hora da última atualização no canto superior direito
  const reps = Object.values(ESTADO_ATUAL.relatorios || {});
  const ultima = reps.length > 0 ? reps[0].atualizado_em : "";
  const lastUpdateTop = document.getElementById("lastUpdateTop");
  if (lastUpdateTop && ultima) {
    lastUpdateTop.textContent = `Última atualização: ${ultima}`;
  }

  Object.keys(ESTADO_ATUAL.relatorios).forEach(repId => {
    renderizarPainelRelatorio(repId);
  });
  renderizarResumoGeral();
}

async function extrairTodos() {
  const btn = document.getElementById("btnExtractAll");
  btn.disabled = true;
  btn.innerHTML = `${ICONS.sync} <span>Sincronizando...</span>`;
  try {
    const res = await fetch("/api/extract-all", {
      method: "POST",
      headers: headersSeguros(true)
    });
    ESTADO_ATUAL = await res.json();
    atualizarInterfaceCompleta();
    iniciarMonitoramentoEnmSegundoPlano();
    mostrarNotificacao("Fontes sincronizadas.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${ICONS.sync} <span>Sincronizar Fontes</span>`;
  }
}

async function extrairUnico(repId) {
  mostrarNotificacao("Sincronizando...");
  const res = await fetch(`/api/extract/${repId}`, {
    method: "POST",
    headers: headersSeguros(true)
  });
  const dadosRep = await res.json();
  ESTADO_ATUAL.relatorios[repId] = dadosRep;
  const lastUpdateTop = document.getElementById("lastUpdateTop");
  if (lastUpdateTop && dadosRep.atualizado_em) {
    lastUpdateTop.textContent = `Última atualização: ${dadosRep.atualizado_em}`;
  }
  renderizarPainelRelatorio(repId);
  renderizarResumoGeral();
  mostrarNotificacao(`${dadosRep.aba_excel} sincronizado.`);
}

async function baixarExcelUnificado() {
  const btn = document.getElementById("btnDownloadExcel");
  btn.disabled = true;
  btn.innerHTML = `${ICONS.download} <span>Baixando...</span>`;

  try {
    const res = await fetch("/api/export-excel", {
      method: "POST",
      headers: headersSeguros(true),
      body: JSON.stringify({
        filtros_por_relatorio: FILTROS_POR_ABA,
        busca_por_relatorio: BUSCA_POR_ABA
      })
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="(.+)"/);
    a.download = match ? match[1] : "Relatorio_Unificado_Vivo.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    mostrarNotificacao("Excel baixado.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${ICONS.download} <span>Baixar Excel</span>`;
  }
}

/* MODAL DE PERFIS E USUÁRIOS (ABERTO AO CLICAR NO USUÁRIO) */
async function abrirModalUsuarios() {
  const modal = document.getElementById("modalUsuarios");
  modal.classList.add("active");
  await carregarPainelUsuariosModal();
}

function fecharModalUsuarios() {
  const modal = document.getElementById("modalUsuarios");
  modal.classList.remove("active");
}

function fecharModalFora(ev) {
  if (ev.target && ev.target.id === "modalUsuarios") {
    fecharModalUsuarios();
  }
}

async function carregarPainelUsuariosModal() {
  const container = document.getElementById("conteudoModalUsuarios");
  const uAtual = ESTADO_ATUAL.usuario || {};

  if (uAtual.perfil !== "administrador") {
    container.innerHTML = `
      <div style="padding:12px 0;font-size:13.5px;">
        <p style="margin-bottom:8px;"><strong>Usuário:</strong> ${uAtual.username}</p>
        <p style="margin-bottom:8px;"><strong>Nome:</strong> ${uAtual.nome}</p>
        <p><strong>Perfil:</strong> ${uAtual.perfil}</p>
      </div>
    `;
    return;
  }

  const res = await fetch("/api/admin/users");
  if (!res.ok) return;
  const data = await res.json();

  const tbodyUsers = (data.usuarios || []).map(u => `
    <tr>
      <td><strong>${u.username}</strong></td>
      <td>${u.nome}</td>
      <td><span class="badge ${u.perfil === 'administrador' ? 'badge-crit' : 'badge-warn'}">${u.perfil.toUpperCase()}</span></td>
      <td>${u.criado_em}</td>
      <td>
        ${u.username !== 'dairon' ? `<button class="btn btn-outline" style="padding:3px 8px;font-size:11px;" onclick="removerUsuarioAdmin('${u.username}')">${ICONS.trash} Remover</button>` : ''}
      </td>
    </tr>
  `).join("");

  container.innerHTML = `
    <form onsubmit="salvarUsuarioAdmin(event)" style="background:#fbf9fc;border:1px solid #e9d5ff;padding:16px;border-radius:10px;margin-bottom:18px;">
      <div class="filter-controls">
        <div class="filter-group">
          <label>Usuário</label>
          <input type="text" id="admUsername" placeholder="Login" required />
        </div>
        <div class="filter-group">
          <label>Nome</label>
          <input type="text" id="admNome" placeholder="Nome completo" required />
        </div>
        <div class="filter-group">
          <label>Perfil</label>
          <select id="admPerfil">
            <option value="usuario">usuario</option>
            <option value="administrador">administrador</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Senha</label>
          <input type="password" id="admPassword" placeholder="Senha" />
        </div>
      </div>
      <div style="margin-top:12px;display:flex;justify-content:flex-end;">
        <button type="submit" class="btn btn-vivo">
          ${ICONS.save}
          <span>Salvar Usuário</span>
        </button>
      </div>
    </form>

    <div class="table-wrapper">
      <table>
        <thead><tr><th>Usuário</th><th>Nome</th><th>Perfil</th><th>Criado em</th><th>Ação</th></tr></thead>
        <tbody>${tbodyUsers}</tbody>
      </table>
    </div>
  `;
}

async function salvarUsuarioAdmin(ev) {
  ev.preventDefault();
  const payload = {
    username: document.getElementById("admUsername").value,
    nome: document.getElementById("admNome").value,
    perfil: document.getElementById("admPerfil").value,
    password: document.getElementById("admPassword").value
  };
  const res = await fetch("/api/admin/users", {
    method: "POST",
    headers: headersSeguros(true),
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    mostrarNotificacao(`Erro: ${data.detail}`);
    return;
  }
  await carregarPainelUsuariosModal();
  mostrarNotificacao(`Usuário '${data.usuario.username}' salvo.`);
}

async function removerUsuarioAdmin(username) {
  const res = await fetch(`/api/admin/users/${username}`, {
    method: "DELETE",
    headers: headersSeguros(true)
  });
  if (res.ok) {
    await carregarPainelUsuariosModal();
    mostrarNotificacao(`Usuário '${username}' removido.`);
  }
}

async function encerrarSessao() {
  await fetch("/api/auth/logout", {
    method: "POST",
    headers: headersSeguros(true)
  });
  window.location.href = "/login";
}

window.addEventListener("DOMContentLoaded", carregarEstadoInicial);
