// Catálogo de Ícones em Silhueta Monocromática Roxo Vivo (#660099)
const ICONS = {
  sync: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74A7.93 7.93 0 004 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>`,
  download: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>`,
  folder: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>`,
  search: `<svg class="icon-vivo" style="width:13px;height:13px;" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>`,
  sliders: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>`,
  alert: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>`,
  lab: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M19.8 18.4L14 10.67V6.5l1.35-1.69c.26-.33.03-.81-.39-.81H9.04c-.42 0-.65.48-.39.81L10 6.5v4.17L4.2 18.4c-.49.66-.02 1.6.8 1.6h14c.82 0 1.29-.94.8-1.6z"/></svg>`,
  building: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>`,
  shield: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>`,
  user: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`,
  terminal: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM7.5 17l-1.41-1.41L9.67 12 6.09 8.41 7.5 7l5 5-5 5zm9.5 0h-6v-2h6v2z"/></svg>`,
  copy: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>`,
  trash: `<svg class="icon-vivo" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`
};

let ESTADO_ATUAL = {
  modo_ambiente: "MOCK",
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
  } else if (abaId === "admin") {
    carregarPainelAdmin();
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
  mostrarNotificacao("Filtros limpos!");
}

function copiarComandoEnm(cmd) {
  navigator.clipboard.writeText(cmd);
  mostrarNotificacao("Comando CLI do Ericsson ENM copiado para a área de transferência!");
}

async function dispararEnmSegundoPlanoManual() {
  mostrarNotificacao("Disparando os 3 comandos CLI no Ericsson ENM em 2º plano...");
  const res = await fetch("/api/enm-cli/run-background", {
    method: "POST",
    headers: headersSeguros(true)
  });
  if (res.ok) {
    const data = await res.json();
    ESTADO_ATUAL.enm_background_job = data.job;
    atualizarBadgeEnmSegundoPlano();
    iniciarMonitoramentoEnmSegundoPlano();
  }
}

function atualizarBadgeEnmSegundoPlano() {
  const job = ESTADO_ATUAL.enm_background_job || {};
  const badge = document.getElementById("enmBgBadge");
  if (!badge) return;

  if (job.em_execucao) {
    badge.innerHTML = `${ICONS.terminal} <span>ENM 2º PLANO: EXECUTANDO (${job.etapa_atual || '...'})</span>`;
  } else {
    badge.innerHTML = `${ICONS.terminal} <span>ENM 2º PLANO: PRONTO (${job.total_alarmes || 0} alarmes)</span>`;
  }

  const statusBox = document.getElementById("enmJobStatusText");
  if (statusBox) {
    statusBox.textContent = job.em_execucao
      ? `Executando em 2º plano: ${job.etapa_atual}`
      : `${job.etapa_atual || 'Concluído'} (Última execução: ${job.ultima_execucao || '-'})`;
  }
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
      atualizarBadgeEnmSegundoPlano();

      if (estavaRodando && !ESTADO_ATUAL.enm_background_job.em_execucao) {
        clearInterval(TIMER_ENM_POLL);
        TIMER_ENM_POLL = null;
        await carregarEstadoInicial();
        mostrarNotificacao("Comandos Ericsson ENM em 2º plano finalizados e consolidados!");
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

async function enviarCliEnmColado() {
  const fonte = document.getElementById("enmFonteSelect").value;
  const texto = document.getElementById("enmCliTextarea").value;
  if (!texto.trim()) {
    mostrarNotificacao("Cole a saída do comando CLI antes de processar.");
    return;
  }
  const res = await fetch("/api/enm-cli/import", {
    method: "POST",
    headers: headersSeguros(true),
    body: JSON.stringify({ fonte, texto })
  });
  const data = await res.json();
  if (!res.ok) {
    mostrarNotificacao(`Erro: ${data.detail}`);
    return;
  }
  ESTADO_ATUAL.relatorios["celldowntime"] = data;
  renderizarPainelRelatorio("celldowntime");
  renderizarResumoGeral();
  mostrarNotificacao(`Saída ENM (${fonte}) processada com PROCV automático!`);
}

function renderizarBlocoEnmCli(rep) {
  if (rep.id !== "celldowntime" || !rep.enm_cli_info) return "";
  const info = rep.enm_cli_info;
  const job = info.background_job || ESTADO_ATUAL.enm_background_job || {};

  const cmdsHtml = Object.entries(info.comandos).map(([fonte, cmd]) => `
    <div class="enm-cmd-row">
      <div><strong style="color:var(--vivo-purple);">[${fonte}]</strong> <span>${cmd}</span></div>
      <button class="btn btn-outline" style="padding:4px 10px;font-size:11px;"
              onclick='copiarComandoEnm(${JSON.stringify(cmd)})'>
        ${ICONS.copy} <span>Copiar CLI</span>
      </button>
    </div>
  `).join("");

  return `
    <div class="enm-box">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div>
          <div style="font-size:13px;font-weight:700;color:var(--vivo-purple);display:flex;align-items:center;gap:6px;">
            ${ICONS.terminal}
            <span>EXECUÇÃO AUTOMÁTICA EM 2º PLANO — ERICSSON ENM CLI (${info.url})</span>
          </div>
          <div id="enmJobStatusText" style="font-size:11.5px;color:var(--text-muted);margin-top:3px;">
            ${job.etapa_atual || 'Worker em 2º plano pronto'} (Última execução: ${job.ultima_execucao || '-'})
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="btn btn-vivo" style="padding:5px 12px;font-size:11.5px;"
                  onclick="dispararEnmSegundoPlanoManual()">
            ${ICONS.sync} <span>Executar Comandos ENM em 2º Plano Agora</span>
          </button>
          <button class="btn btn-outline" style="padding:5px 12px;font-size:11.5px;"
                  onclick="const el=document.getElementById('enmPasteArea');el.style.display=el.style.display==='none'?'block':'none';">
            ${ICONS.terminal} <span>Colar Saída Manual CLI</span>
          </button>
        </div>
      </div>
      ${cmdsHtml}
      <div id="enmPasteArea" style="display:none;margin-top:12px;padding-top:12px;border-top:1px dashed #c084fc;">
        <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;">
          <label style="font-size:12px;font-weight:700;color:var(--vivo-purple);">Comando Referente:</label>
          <select id="enmFonteSelect" style="padding:6px 10px;border-radius:6px;border:1px solid #d1d5db;">
            <option value="P1">P1 (Heartbeat Failure CRITICAL)</option>
            <option value="4G_5G">4G_5G (EUtranCell / NRCellDU MAJOR)</option>
            <option value="3G">3G (RNC UtranCell MAJOR)</option>
          </select>
          <button class="btn btn-vivo" style="padding:6px 14px;" onclick="enviarCliEnmColado()">
            Processar e Cruzar com Grid 4G/5G/3G
          </button>
        </div>
        <textarea id="enmCliTextarea" rows="4" style="width:100%;padding:8px;border-radius:6px;border:1px solid #d1d5db;font-family:monospace;font-size:12px;"
                  placeholder="Cole aqui o Ctrl+V do clipboard do Ericsson ENM CLI..."></textarea>
      </div>
    </div>
  `;
}

function renderizarPainelRelatorio(repId) {
  const rep = ESTADO_ATUAL.relatorios[repId];
  const container = document.getElementById(`panel-${repId}`);
  if (!rep || !container) return;

  const isAdmin = ESTADO_ATUAL.usuario.perfil === "administrador";
  const filtrosDisp = rep.filtros_disponiveis || {};
  const selecoesAtuais = FILTROS_POR_ABA[repId] || {};
  const buscaAtual = BUSCA_POR_ABA[repId] || "";

  let controlesFiltroHtml = `
    <div class="filter-group">
      <label>${ICONS.search} <span>Busca Livre</span></label>
      <input type="text" placeholder="Pesquisar em qualquer coluna..." value="${buscaAtual}"
             oninput="atualizarBusca('${repId}', this.value)" />
    </div>
  `;

  for (const [col, valores] of Object.entries(filtrosDisp)) {
    const valorSelecionado = selecoesAtuais[col] || "TODOS";
    const optionsHtml = [`<option value="TODOS">Todos (${valores.length})</option>`]
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

  const botaoUploadHtml = isAdmin ? `
    <label class="btn btn-outline" style="cursor:pointer;">
      ${ICONS.folder}
      <span>Importar Base Bruta (.xlsx/.xlsm/.csv)</span>
      <input type="file" accept=".xlsx,.xlsm,.xls,.csv,.json" style="display:none"
             onchange="fazerUploadManual('${repId}', this.files[0])" />
    </label>
  ` : "";

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">${rep.nome} — <span style="color:var(--vivo-purple)">Nome da Planilha no Excel: ${rep.aba_excel}</span></div>
          <small style="color:var(--text-muted)">Origem: ${rep.origem} | Última leitura: ${rep.atualizado_em}</small>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          ${botaoUploadHtml}
          <button class="btn btn-vivo" onclick="extrairUnico('${repId}')">
            ${ICONS.sync}
            <span>Sincronizar ${rep.aba_excel}</span>
          </button>
        </div>
      </div>

      ${rep.erro ? `<div style="background:#f5ebf9;color:#4a0070;border:1px solid #660099;padding:12px;border-radius:8px;margin-bottom:14px;font-size:13px;display:flex;align-items:center;gap:8px;">${ICONS.alert} <span>${rep.erro}</span></div>` : ""}

      ${renderizarBlocoEnmCli(rep)}

      <div class="filter-bar">
        <div class="filter-bar-header">
          <span style="display:flex;align-items:center;gap:8px;">
            ${ICONS.sliders}
            <span>FILTROS ESPECÍFICOS (${rep.aba_excel}) — Colunas idênticas à pasta "formatado/"</span>
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

async function salvarEdicaoCelula(repId, rowIdx, coluna, valor) {
  await fetch("/api/cell-edit", {
    method: "POST",
    headers: headersSeguros(true),
    body: JSON.stringify({ report_id: repId, row_idx: rowIdx, coluna, valor })
  });
  const rep = ESTADO_ATUAL.relatorios[repId];
  if (rep && rep.registros) {
    const item = rep.registros.find(r => r._row_idx === rowIdx);
    if (item) item[coluna] = valor;
  }
}

function formatarCelula(repId, rowIdx, col, val, editaveis) {
  const s = String(val ?? "");
  if (editaveis && editaveis.includes(col)) {
    const safeVal = s.replace(/"/g, "&quot;");
    return `<input type="text" class="cell-input" value="${safeVal}" placeholder="Preencher..."
                   onchange="salvarEdicaoCelula('${repId}', ${rowIdx}, '${col}', this.value)" />`;
  }
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
  if (countEl) countEl.textContent = `${filtrados.length}/${rep.registros.length}`;

  const tableContainer = document.getElementById(`table-container-${repId}`);
  if (!tableContainer) return;

  if (filtrados.length === 0) {
    tableContainer.innerHTML = `<div style="padding:24px;text-align:center;color:var(--text-muted);">Nenhum registro encontrado com os filtros atuais.</div>`;
    return;
  }

  const cols = rep.colunas || [];
  const editaveis = rep.colunas_editaveis || [];
  const thead = `<thead><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr></thead>`;
  const tbody = `<tbody>${filtrados.map(row => `
    <tr>${cols.map(c => `<td title="${String(row[c] ?? "").replace(/"/g, '&quot;')}">${formatarCelula(repId, row._row_idx, c, row[c], editaveis)}</td>`).join("")}</tr>
  `).join("")}</tbody>`;

  tableContainer.innerHTML = `<table>${thead}${tbody}</table>`;
}

function renderizarResumoGeral() {
  const reps = ESTADO_ATUAL.relatorios;
  const ids = Object.keys(reps);
  if (ids.length === 0) return;

  let totalBrutoGeral = 0;
  let totalFiltradoGeral = 0;
  let kpiHtml = "";

  ids.forEach(repId => {
    const r = reps[repId];
    const filtrados = obterRegistrosFiltrados(repId);
    totalBrutoGeral += r.registros.length;
    totalFiltradoGeral += filtrados.length;

    const filtrosAtivos = Object.entries(FILTROS_POR_ABA[repId] || {})
      .filter(([_, v]) => v && v !== "TODOS")
      .map(([k, v]) => `${k}: ${v}`)
      .join(" | ");

    kpiHtml += `
      <div class="kpi-card">
        <h3>Planilha: ${r.aba_excel} (${r.nome})</h3>
        <div class="kpi-value">${filtrados.length} <span style="font-size:14px;font-weight:500;color:var(--text-muted)">/ ${r.registros.length} brutos</span></div>
        <div class="kpi-meta">
          <span>${filtrosAtivos || "Exibindo base completa"}</span>
          <a href="javascript:void(0)" onclick="trocarAba('${repId}')" style="color:var(--vivo-purple);font-weight:600;text-decoration:none;">Abrir ${r.aba_excel} →</a>
        </div>
      </div>
    `;
  });

  kpiHtml = `
    <div class="kpi-card">
      <h3>Resumo Online (Não vai no Excel Exportado)</h3>
      <div class="kpi-value">${totalFiltradoGeral} <span style="font-size:14px;font-weight:500;color:var(--text-muted)">registros filtrados</span></div>
      <div class="kpi-meta">
        <span>Total bruto: ${totalBrutoGeral}</span>
        <span>Excel contém: P1, AnelComutado, CellDowntime</span>
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
          <th>UF / Estado</th>
          ${ids.map(id => `<th>${reps[id].aba_excel}</th>`).join("")}
          <th>Total na UF</th>
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

  // Quebra Operacional
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
            ${r.aba_excel} — ${r.nome} (por ${colChave})
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
  const badge = document.getElementById("envBadge");
  if (ESTADO_ATUAL.modo_ambiente === "MOCK") {
    badge.innerHTML = `${ICONS.lab} <span>MODO LOCAL (BASES BRUTAS/FORMATADAS)</span>`;
  } else {
    badge.innerHTML = `${ICONS.building} <span>MODO PRODUÇÃO (REDE VIVO)</span>`;
  }

  atualizarBadgeEnmSegundoPlano();

  const u = ESTADO_ATUAL.usuario || {};
  const userBadge = document.getElementById("userBadge");
  userBadge.innerHTML = `${u.perfil === "administrador" ? ICONS.shield : ICONS.user} <span>${u.nome} (${u.perfil.toUpperCase()})</span>`;

  const tabAdmin = document.getElementById("tabbtn-admin");
  if (tabAdmin) {
    tabAdmin.style.display = u.perfil === "administrador" ? "flex" : "none";
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
    mostrarNotificacao("Fontes sincronizadas e comandos ENM disparados em 2º plano!");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${ICONS.sync} <span>Sincronizar Fontes</span>`;
  }
}

async function extrairUnico(repId) {
  mostrarNotificacao(`Sincronizando ${repId}...`);
  const res = await fetch(`/api/extract/${repId}`, {
    method: "POST",
    headers: headersSeguros(true)
  });
  const dadosRep = await res.json();
  ESTADO_ATUAL.relatorios[repId] = dadosRep;
  renderizarPainelRelatorio(repId);
  renderizarResumoGeral();
  mostrarNotificacao(`Planilha ${dadosRep.aba_excel} sincronizada!`);
}

async function fazerUploadManual(repId, file) {
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  mostrarNotificacao(`Importando e formatando ${file.name}...`);

  const res = await fetch(`/api/upload/${repId}`, {
    method: "POST",
    headers: headersSeguros(false),
    body: formData
  });
  if (!res.ok) {
    const err = await res.json();
    mostrarNotificacao(`Erro: ${err.detail}`);
    return;
  }
  const dadosRep = await res.json();
  ESTADO_ATUAL.relatorios[repId] = dadosRep;
  FILTROS_POR_ABA[repId] = {};
  renderizarPainelRelatorio(repId);
  renderizarResumoGeral();
  mostrarNotificacao(`Base ${file.name} convertida para a planilha ${dadosRep.aba_excel}!`);
}

async function baixarExcelUnificado() {
  const btn = document.getElementById("btnDownloadExcel");
  btn.disabled = true;
  btn.innerHTML = `${ICONS.download} <span>Gerando Excel...</span>`;

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
    mostrarNotificacao("Excel baixado contendo exclusivamente as abas: P1, AnelComutado e CellDowntime!");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${ICONS.download} <span>Baixar Excel (P1, AnelComutado, CellDowntime)</span>`;
  }
}

async function carregarPainelAdmin() {
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
        ${u.username !== 'dairon' ? `<button class="btn btn-outline" style="padding:3px 8px;font-size:11px;" onclick="removerUsuarioAdmin('${u.username}')">${ICONS.trash} Remover</button>` : '<small style="color:var(--text-muted)">Principal</small>'}
      </td>
    </tr>
  `).join("");

  document.getElementById("tabelaUsuariosAdmin").innerHTML = `
    <table>
      <thead><tr><th>Usuário</th><th>Nome</th><th>Perfil RBAC</th><th>Criado em</th><th>Ação</th></tr></thead>
      <tbody>${tbodyUsers}</tbody>
    </table>
  `;

  const tbodyAudit = (data.auditoria || []).map(ev => `
    <tr>
      <td>${ev.timestamp}</td>
      <td><strong>${ev.usuario}</strong></td>
      <td>${ev.perfil}</td>
      <td><span class="badge badge-warn">${ev.acao}</span></td>
      <td>${ev.detalhes}</td>
    </tr>
  `).join("");

  document.getElementById("tabelaAuditoriaAdmin").innerHTML = `
    <table>
      <thead><tr><th>Data/Hora</th><th>Usuário</th><th>Perfil</th><th>Evento</th><th>Detalhes</th></tr></thead>
      <tbody>${tbodyAudit || '<tr><td colspan="5">Sem eventos registrados.</td></tr>'}</tbody>
    </table>
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
  document.getElementById("admPassword").value = "";
  carregarPainelAdmin();
  mostrarNotificacao(`Usuário '${data.usuario.username}' salvo com sucesso!`);
}

async function removerUsuarioAdmin(username) {
  const res = await fetch(`/api/admin/users/${username}`, {
    method: "DELETE",
    headers: headersSeguros(true)
  });
  if (res.ok) {
    carregarPainelAdmin();
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
