const app = document.getElementById("app");

const state = {
  page: "overview",
  search: "",
  selectedByModule: { technical: null, seo: null, tagging: null, sitemap: null },
  moduleFilters: {
    sitemap: { url: "", severity: "all" },
    technical: { url: "", severity: "all" },
    seo: { url: "", severity: "all" },
    tagging: { url: "", severity: "all" }
  }
};

const COLUMN_LABELS = {
  page_url: "URL", normalized_path: "Ruta", url_type: "Tipo de página", page_group: "Grupo de negocio",
  is_priority: "Prioritaria", should_audit: "Auditar", status_code: "Código HTTP", response_time_ms: "Tiempo de respuesta",
  http_status: "HTTP Status", redirect_type: "Tipo Redirect", final_url: "URL Final", is_valid_status: "Estado válido", sitemap_issue: "Problema Sitemap",
  redirect_count: "Redirecciones", crawl_status: "Estado técnico", mobile_context: "Contexto mobile", has_title: "Título",
  has_meta_description: "Meta descripción", h1_count: "Encabezados H1", has_canonical: "Canonical",
  canonical_url: "URL canónica", has_noindex: "Noindex",
  has_lang: "Idioma", images_without_alt: "Imágenes sin ALT", has_gtm: "GTM", has_ga4: "GA4", has_datalayer: "dataLayer",
  cta_elements_count: "CTAs", form_elements_count: "Formularios", has_interactions: "Interacciones", has_generate_lead_hint: "Genera lead",
  has_whatsapp_click_hint: "WhatsApp", double_tagging_detected: "Doble etiquetado", finding_code: "Código", finding_detail: "Hallazgo",
  severity: "Severidad", recommendation: "Recomendación", action: "Acción", lang: "Idioma", title: "Título", meta_description: "Meta descripción",
  component_type: "Componente", component_id: "ID componente", component_selector: "Selector", html_section: "Sección HTML", element_value: "Valor actual", expected_value: "Valor esperado"
};

const moduleConfig = {
  sitemap: { title: "Módulo 1 · Sitemap", subtitle: "Review and manage the foundational URL structure for the audit process.", latest: "/api/modules/sitemap/latest", kpis: id => `/api/modules/sitemap/runs/${id}/kpis`, results: id => `/api/modules/sitemap/runs/${id}/urls?limit=100` },
  technical: { title: "Módulo 2 · Técnico", subtitle: "Análisis de códigos de estado, latencia y arquitectura del servidor.", latest: "/api/modules/technical/latest", results: id => `/api/modules/technical/runs/${id}/results?limit=100`, findings: id => `/api/modules/technical/runs/${id}/findings?limit=100` },
  seo: { title: "Módulo 3 · SEO", subtitle: "Análisis de etiquetas meta, directivas de indexación y estructura de contenido.", latest: "/api/modules/seo/latest", kpis: id => `/api/modules/seo/runs/${id}/kpis`, results: id => `/api/modules/seo/runs/${id}/results?limit=100`, findings: id => `/api/modules/seo/runs/${id}/findings?limit=100` },
  tagging: { title: "Módulo 4 · Tagging", subtitle: "Análisis de implementación de etiquetas, GA4, GTM y dataLayer.", latest: "/api/modules/tagging/latest", results: id => `/api/modules/tagging/runs/${id}/results?limit=100`, findings: id => `/api/modules/tagging/runs/${id}/findings?limit=100` }
};

document.querySelectorAll(".nav[data-page]").forEach(btn => btn.onclick = () => {
  document.querySelectorAll(".nav").forEach(x => x.classList.remove("active"));
  btn.classList.add("active");
  state.page = btn.dataset.page;
  render();

});

document.getElementById("refresh").onclick = () => render();
document.getElementById("search").oninput = e => { state.search = e.target.value.toLowerCase().trim(); render(); };
const sidebarToggle = document.getElementById("toggleSidebar");
sidebarToggle?.addEventListener("click", () => {
  document.body.classList.toggle("sidebar-collapsed");
  const collapsed = document.body.classList.contains("sidebar-collapsed");
  sidebarToggle.title = collapsed ? "Expandir sidebar" : "Comprimir sidebar";
  sidebarToggle.setAttribute("aria-label", collapsed ? "Expandir sidebar" : "Comprimir sidebar");
  const iconEl = sidebarToggle.querySelector(".material-symbols-outlined");
  if (iconEl) iconEl.textContent = collapsed ? "right_panel_open" : "left_panel_close";
});


const fmt = v => (v === null || v === undefined || v === "") ? "—" : (Number.isFinite(Number(v)) ? Number(v).toLocaleString("es-PE") : v);
const safe = (v, fb = "—") => (v === null || v === undefined || v === "") ? fb : v;
const shortUrl = (v = "") => String(v).replace("https://www.claro.com.pe", "");
const icon = name => `<span class="material-symbols-outlined">${name}</span>`;
const ms = v => (v === null || v === undefined || v === "") ? "—" : `${Math.round(Number(v))} ms`;
const pct = (rows, field) => !rows?.length ? "0%" : `${Math.round((rows.filter(r => Boolean(r[field])).length / rows.length) * 100)}%`;
const count = (rows, pred) => (rows || []).filter(pred).length;
const filtered = rows => !state.search ? (rows || []) : (rows || []).filter(r => JSON.stringify(r).toLowerCase().includes(state.search));
const runDateCandidates = ["executed_at","execution_datetime","execution_date","run_datetime","run_date","created_at","updated_at","processed_at","timestamp"];

function parseRunDate(source){
  if(!source || typeof source !== "object") return null;
  for(const key of runDateCandidates){
    if(source[key]){
      const d = new Date(source[key]);
      if(!Number.isNaN(d.getTime())) return d;
    }
  }
  return null;
}


function setRunChip(dateValue){
  const chip = document.querySelector(".run-chip");
  if(!chip) return;
  if(!dateValue){ chip.textContent = "Última corrida"; return; }
  const d = new Date(dateValue);
  if(Number.isNaN(d.getTime())){ chip.textContent = "Última corrida"; return; }
  const pretty = d.toLocaleString("es-PE", { dateStyle: "short", timeStyle: "short" });
  chip.textContent = `Última corrida: ${pretty}`;
}


const scoreTone = n => n >= 90 ? "ok" : n >= 70 ? "warn" : "bad";
const sevNorm = s => String(s || "").toLowerCase().includes("alta") ? "Alta" : String(s || "").toLowerCase().includes("media") ? "Media" : "Baja";

function techScore(rows){ if(!rows?.length) return 100; const err=count(rows,r=>Number(r.status_code)>=400); const slow=count(rows,r=>Number(r.response_time_ms)>1000); const red=count(rows,r=>Number(r.redirect_count)>2); return Math.max(0,Math.round(100-(err/rows.length*45+slow/rows.length*30+red/rows.length*25))); }
function seoScore(rows){ if(!rows?.length) return 100; const missT=count(rows,r=>!r.has_title), missD=count(rows,r=>!r.has_meta_description), missC=count(rows,r=>!r.has_canonical), noi=count(rows,r=>r.has_noindex && String(r.page_group).toLowerCase().includes("comercial")), alt=(rows.reduce((a,r)=>a+Number(r.images_without_alt||0),0)/rows.length); return Math.max(0,Math.round(100-(missT/rows.length*20+missD/rows.length*20+missC/rows.length*20+noi/rows.length*20+Math.min(20,alt)))); }
function taggingScore(rows){ if(!rows?.length) return 100; const noG=count(rows,r=>!r.has_gtm), noA=count(rows,r=>!r.has_ga4), noD=count(rows,r=>!r.has_datalayer), dbl=count(rows,r=>r.double_tagging_detected); return Math.max(0,Math.round(100-(noG/rows.length*25+noA/rows.length*25+noD/rows.length*25+dbl/rows.length*25))); }

function trafficBadge(cls, text){ return `<span class="traffic ${cls}"><i></i>${text}</span>`; }
function pillSeverity(v){ const s=sevNorm(v); const cls=s==="Alta"?"bad":s==="Media"?"warn":"ok"; return trafficBadge(cls, s); }
function pillHttp(v){ const n=Number(v); const cls=n===200?"ok":(n===301||n===302)?"warn":"bad"; return trafficBadge(cls, `HTTP ${safe(v)}`); }
function pillLatency(v){ const n=Number(v); const cls=n<400?"ok":n<=1000?"warn":"bad"; const txt=n<400?"Bueno":n<=1000?"Medio":"Alto"; return trafficBadge(cls, `${ms(v)} · ${txt}`); }
function pillRedirect(v){ const n=Number(v||0); const cls=n===0?"ok":n<=2?"warn":"bad"; return trafficBadge(cls, `${n}`); }
function boolIcon(v){ return v?`<span class="bool ok">${icon("check_circle")}</span>`:`<span class="bool bad">${icon("cancel")}</span>`; }

function renderCell(row,col){
  const v=row[col];
  if(col==="status_code"||col==="http_status") return pillHttp(v);
  if(col==="response_time_ms") return pillLatency(v);
  if(col==="redirect_count") return pillRedirect(v);
  if(col==="severity") return pillSeverity(v);
  if(col==='is_valid_status') return v===false?trafficBadge('bad','Requiere corrección'):trafficBadge('ok','Válido');
  if(typeof v === "boolean") return boolIcon(v);
  if(col.includes("url")) return `<span class="url-cell" title="${safe(v)}">${shortUrl(v||"—")}</span>`;
  if(col==='sitemap_issue') return v?`<span title='${safe(v)}'>⚠ ${safe(v)}</span>`:'-';
  return safe(v,'-');
}


function table(rows, columns, moduleKey){
  const data=filtered(rows);
  const cols=[...columns,"action"];
  return `<div class="table-card"><div class="table-wrap"><table><thead><tr>${cols.map(c=>`<th title="${c}">${COLUMN_LABELS[c]||c}</th>`).join("")}</tr></thead><tbody>${data.length?data.map((r,i)=>`<tr><td>${columns.map(c=>renderCell(r,c)).join("</td><td>")}</td><td><button class="link-button" data-action="detail" data-module="${moduleKey}" data-row="${i}">${icon("open_in_new")} Ver detalles</button></td></tr>`).join(""):`<tr><td class="empty-cell" colspan="${cols.length}">Sin datos para mostrar</td></tr>`}</tbody></table></div></div>`;
}

function moduleFiltersUI(moduleKey){
  const f = state.moduleFilters[moduleKey] || { url: "", severity: "all" };
  return `<div class="findings-filters">
    <input id="f-url-${moduleKey}" placeholder="Filtrar por URL" value="${f.url}" />
    <select id="f-sev-${moduleKey}">
      <option value="all">Severidad: Todas</option><option value="Alta">Alta</option><option value="Media">Media</option><option value="Baja">Baja</option>
    </select>
  </div>`;
}

function applyModuleFilters(rows, moduleKey){
  const f = state.moduleFilters[moduleKey] || { url: "", severity: "all" };
  return (rows || []).filter(r => {
    const u = !f.url || String(r.page_url || "").toLowerCase().includes(f.url);
    const sev = f.severity === "all" || sevNorm(r.severity) === f.severity;
    return u && sev;
  });
}

function pageHeader(title,subtitle,actions=""){ return `<div class="page-header"><div><h1>${title}</h1><p>${subtitle}</p></div><div class="page-actions">${actions}</div></div>`; }
function kpiCard({title,value,subtitle="",tone="default",iconName="analytics"}){ return `<article class="audit-card kpi-card ${tone}"><div class="kpi-top"><span>${title}</span>${icon(iconName)}</div><div class="kpi-value">${value}</div>${subtitle?`<div class="kpi-subtitle">${subtitle}</div>`:""}</article>`; }
function panel(title,content,action=""){ return `<section class="audit-panel"><div class="panel-header"><h2>${title}</h2>${action}</div><div class="panel-body">${content}</div></section>`; }

function findingsSummary(findings){
  const sev={Alta:0,Media:0,Baja:0}; const byCode={};
  (findings||[]).forEach(f=>{ const s=sevNorm(f.severity); sev[s]++; const code=safe(f.finding_code,'Hallazgo'); byCode[code]=(byCode[code]||0)+1; });
  const top=Object.entries(byCode).sort((a,b)=>b[1]-a[1]).slice(0,6);
  return `<div class="summary-card"><div class="sev-grid">${Object.entries(sev).map(([k,v])=>`<div>${pillSeverity(k)} <strong>${v}</strong></div>`).join("")}</div><div class="finding-code-list">${top.length?top.map(([k,v])=>`<div class="summary-line"><span title="${k}">${k}</span><strong>${v}</strong></div>`).join(""):`<div class="empty-box">Sin hallazgos detectados.</div>`}</div></div>`;
}

function recommendationsFor(url, findings){
  const list=(findings||[]).filter(f=>String(f.page_url||"")===String(url||"")).map(f=>safe(f.recommendation)).filter(Boolean);
  return `<div class="recommend-box">${list.length?`<ul>${list.map(x=>`<li>${x}</li>`).join("")}</ul>`:"Sin recomendaciones pendientes para esta URL en la corrida actual."}</div>`;
}

function findingsTable(findings,moduleKey){
  return table(findings||[],['page_url','finding_code','severity','finding_detail','recommendation','component_type','component_id','component_selector','html_section','element_value','expected_value'],moduleKey);
}

function bindDetailButtons(rows,moduleKey){
  document.querySelectorAll(`button[data-action='detail'][data-module='${moduleKey}']`).forEach(btn=>btn.onclick=()=>{ state.selectedByModule[moduleKey]=filtered(rows)[Number(btn.dataset.row)]?.page_url||null; render(); });
}

function bindModuleFilters(moduleKey){
  document.getElementById(`f-url-${moduleKey}`)?.addEventListener("input", e => { state.moduleFilters[moduleKey].url = e.target.value.toLowerCase().trim(); render(); });
  const s = document.getElementById(`f-sev-${moduleKey}`);
  if (s) { s.value = state.moduleFilters[moduleKey].severity; s.addEventListener("change", e => { state.moduleFilters[moduleKey].severity = e.target.value; render(); }); }
}

async function render(){
  app.innerHTML=`<div class="loading-card">${icon("hourglass_empty")} Cargando información...</div>`;
  if(state.page==="overview") return renderOverview();
  if(state.page==="sitemap") return renderSitemap();
  if(state.page==="technical") return renderTechnical();
  if(state.page==="seo") return renderSeo();
  if(state.page==="tagging") return renderTagging();
}


async function renderOverview(){
  const d=await apiGet('/api/overview/latest', null); if(!d) return app.innerHTML=`<div class='empty-box'>No se pudo cargar resumen.</div>`;
  setRunChip(parseRunDate(d));
  const s=d.sitemap||{}, t=d.technical||{}, seo=d.seo||{}, tag=d.tagging||{};
  const health=Math.round((Number(t.health_score||100)+Number(seo.health_score||100)+Number(tag.health_score||100))/3);
  app.innerHTML=`<div class='page'>${pageHeader('Resumen General','Visión global del estado de la auditoría actual.',`<span class='updated'>${icon('update')} Última actualización disponible</span>`)}
    <div class='kpi-grid overview-grid'>
      ${kpiCard({title:'URLs leídas',value:fmt(s.total_urls_found),iconName:'link'})}
      ${kpiCard({title:'URLs auditables',value:fmt(s.total_urls_ready_for_audit),iconName:'fact_check',tone:'success'})}
      ${kpiCard({title:'Hallazgos técnicos',value:fmt(t.total_urls_error||0),iconName:'bug_report',tone:t.total_urls_error?'danger':'success'})}
      ${kpiCard({title:'Hallazgos SEO',value:fmt(seo.total_urls_error||0),iconName:'search',tone:seo.total_urls_error?'danger':'success'})}
      ${kpiCard({title:'Hallazgos tagging',value:fmt(tag.total_urls_error||0),iconName:'label',tone:tag.total_urls_error?'danger':'success'})}
      ${kpiCard({title:'Health score general',value:`${health}%`,iconName:'monitoring',tone:scoreTone(health)==='ok'?'success':scoreTone(health)==='warn'?'warning':'danger'})}
    </div>


    <div class='dashboard-grid'>
      ${panel('Última corrida por módulo',`<div class='run-list'>${runRow('M1 · Sitemap',s.run_id,s.execution_status)}${runRow('M2 · Técnico',t.run_id,t.execution_status)}${runRow('M3 · SEO',seo.run_id,seo.execution_status)}${runRow('M4 · Tagging',tag.run_id,tag.execution_status)}</div>`)}
      ${panel('Hallazgos detectados',findingsSummary([...(t.findings||[]),...(seo.findings||[]),...(tag.findings||[])]))}
    </div></div>`;
}

function runRow(label,id,status){
  const ok = String(status || "").toLowerCase().includes("success");
  return `

    <div class="run-row">
      <div class="run-main">
        <strong>${label}</strong>
        <code title="${safe(id)}">${safe(id)}</code>
      </div>

      <div class="run-status">
        ${trafficBadge(ok ? "ok" : "warn", ok ? "Success" : safe(status))}
      </div>
    </div>
  `;
}

async function renderSitemap(){
  const latest=await apiGet(moduleConfig.sitemap.latest,null); if(!latest?.run_id) return app.innerHTML=`<div class='empty-box'>No hay corridas de sitemap.</div>`;
  setRunChip(parseRunDate(latest));
  const kpis=await apiGet(moduleConfig.sitemap.kpis(latest.run_id),{});
  const rows=await apiGet(moduleConfig.sitemap.results(latest.run_id),[]);
  const filteredRows = applyModuleFilters(rows, "sitemap");
  app.innerHTML=`<div class='page'>${pageHeader(moduleConfig.sitemap.title,moduleConfig.sitemap.subtitle)}
    <div class='kpi-grid overview-grid'>
      ${kpiCard({title:'Total URLs',value:fmt(kpis?.total_urls ?? rows.length),iconName:'link'})}
      ${kpiCard({title:'URLs 200 OK',value:fmt(kpis?.urls_status_200 ?? count(rows,r=>Number(r.http_status)===200)),iconName:'check_circle',tone:'success'})}
      ${kpiCard({title:'URLs 301',value:fmt(kpis?.urls_status_301 ?? count(rows,r=>Number(r.http_status)===301)),iconName:'redo',tone:'warning'})}
      ${kpiCard({title:'URLs 302',value:fmt(kpis?.urls_status_302 ?? count(rows,r=>Number(r.http_status)===302)),iconName:'swap_horiz',tone:'warning'})}
      ${kpiCard({title:'Errores 4xx/5xx',value:fmt(kpis?.urls_status_4xx_5xx ?? count(rows,r=>Number(r.http_status)>=400)),iconName:'error',tone:'danger'})}
      ${kpiCard({title:'URLs inválidas',value:fmt(kpis?.urls_invalid_status ?? count(rows,r=>r.is_valid_status===false)),iconName:'report',tone:'danger'})}
    </div>

    ${panel('Validación de sitemap', `<div class='empty-box'>Un sitemap debe contener URLs finales válidas con HTTP 200. Las URLs con redirecciones 301/302 o errores 4xx/5xx deben corregirse, reemplazarse por su URL final o retirarse del sitemap.</div>`)}
    ${panel('Vista principal',`${moduleFiltersUI('sitemap')}${table(filteredRows,['page_url','normalized_url','normalized_path','url_type','page_group','is_priority','should_audit','http_status','redirect_type','final_url','is_valid_status','sitemap_issue'],'sitemap')}`)}</div>`;
  bindModuleFilters("sitemap");
}

async function renderTechnical(){
  const latest=await apiGet(moduleConfig.technical.latest,null); if(!latest?.run_id) return app.innerHTML=`<div class='empty-box'>No hay corridas técnicas.</div>`;
  setRunChip(parseRunDate(latest));
  const rows=await apiGet(moduleConfig.technical.results(latest.run_id),[]); const findings=await apiGet(moduleConfig.technical.findings(latest.run_id),[]);
  const filteredRows = applyModuleFilters(rows, "technical");
  const score=techScore(rows); const sel=rows.find(r=>r.page_url===state.selectedByModule.technical)||filteredRows[0];
  app.innerHTML=`<div class='page'>${pageHeader(moduleConfig.technical.title,moduleConfig.technical.subtitle)}<div class='module-layout technical-layout'><div class='main-column'>
    <div class='kpi-grid technical-kpis'>${kpiCard({title:'URLs procesadas',value:fmt(latest.total_urls_processed),iconName:'language'})}${kpiCard({title:'Status OK',value:fmt(latest.total_urls_ok),iconName:'check_circle',tone:'success'})}${kpiCard({title:'Errores HTTP',value:fmt(latest.total_urls_error),iconName:'error',tone:Number(latest.total_urls_error)?'danger':'success'})}${kpiCard({title:'Technical Health Score',value:`${score}%`,iconName:'monitoring',tone:scoreTone(score)==='ok'?'success':scoreTone(score)==='warn'?'warning':'danger'})}</div>
    ${panel('Resultados técnicos',`<div class='legend-row'>${trafficBadge('ok','Verde: bueno')} ${trafficBadge('warn','Amarillo: medio')} ${trafficBadge('bad','Rojo: alerta')}</div>${moduleFiltersUI('technical')}${table(filteredRows,['page_url','status_code','response_time_ms','redirect_count','crawl_status'],'technical')}`)}${panel('Hallazgos técnicos', findingsTable(findings,'tech-findings'))}</div>
    <aside class='detail-drawer'>${panel('Detalle de URL',sel?detailTechnical(sel,findings):`<div class='empty-box'>Selecciona una URL.</div>`,sel?`<button class='button' id='closeDetailTech'>Cerrar</button>`:'')}</aside></div></div>`;
  bindDetailButtons(rows,'technical'); document.getElementById('closeDetailTech')?.addEventListener('click',()=>{state.selectedByModule.technical=null; render();});
  bindModuleFilters("technical");
}


function detailTechnical(r, findings){ return `<div class='detail-card'>${summaryLine('URL',`<a class='detail-url' target='_blank' href='${safe(r.page_url,'#')}'>${safe(r.page_url)}</a>`)}${summaryLine('Código HTTP',pillHttp(r.status_code))}${summaryLine('Tiempo de respuesta',pillLatency(r.response_time_ms))}${summaryLine('Redirecciones',pillRedirect(r.redirect_count))}${summaryLine('Estado crawl',safe(r.crawl_status))}${summaryLine('Contexto mobile',safe(r.mobile_context))}<h3>Recomendaciones</h3>${recommendationsFor(r.page_url,findings)}</div>`; }

async function renderSeo(){
  const latest=await apiGet(moduleConfig.seo.latest,null); if(!latest?.run_id) return app.innerHTML=`<div class='empty-box'>No hay corridas SEO.</div>`;
  setRunChip(parseRunDate(latest));
  const kpis=await apiGet(moduleConfig.seo.kpis(latest.run_id),{});
  const rows=await apiGet(moduleConfig.seo.results(latest.run_id),[]); const findings=await apiGet(moduleConfig.seo.findings(latest.run_id),[]);
  const filteredRows = applyModuleFilters(rows, "seo");
  const missT=kpis?.titles_too_short ?? count(findings,r=>r.finding_code==='SEO_TITLE_TOO_SHORT');
  const longT=kpis?.titles_too_long ?? count(findings,r=>r.finding_code==='SEO_TITLE_TOO_LONG');
  const missD=kpis?.metas_too_short ?? count(findings,r=>r.finding_code==='SEO_META_TOO_SHORT');
  const longD=kpis?.metas_too_long ?? count(findings,r=>r.finding_code==='SEO_META_TOO_LONG');
  const noH1=kpis?.pages_without_h1 ?? count(findings,r=>r.finding_code==='SEO_H1_MISSING');
  const multiH1=kpis?.pages_with_multiple_h1 ?? count(findings,r=>r.finding_code==='SEO_H1_MULTIPLE');
  const dupH1=count(findings,r=>r.finding_code==='SEO_H1_DUPLICATED');
  const missC=count(rows,r=>!r.has_canonical), noi=count(rows,r=>r.has_noindex&&String(r.page_group).toLowerCase().includes('comercial')); const score=seoScore(rows);
  const sel=rows.find(r=>r.page_url===state.selectedByModule.seo)||filteredRows[0];
  app.innerHTML=`<div class='page'>${pageHeader(moduleConfig.seo.title,moduleConfig.seo.subtitle)}<div class='module-layout technical-layout'><div class='main-column'>
    <div class='kpi-grid overview-grid'>${kpiCard({title:'Total páginas',value:fmt(kpis?.total_pages ?? rows.length),iconName:'web'})}${kpiCard({title:'Páginas sin H1',value:fmt(noH1),iconName:'title',tone:noH1?'danger':'success'})}${kpiCard({title:'Titles muy cortos',value:fmt(missT),iconName:'short_text',tone:missT?'warning':'success'})}${kpiCard({title:'Titles muy largos',value:fmt(longT),iconName:'subject',tone:longT?'warning':'success'})}${kpiCard({title:'Meta cortas',value:fmt(missD),iconName:'text_fields',tone:missD?'warning':'success'})}${kpiCard({title:'Meta largas',value:fmt(longD),iconName:'article',tone:longD?'warning':'success'})}</div>${panel('Errores de H1', `<div class='sev-grid'><div>${trafficBadge('bad','H1 faltante')} <strong>${fmt(noH1)}</strong></div><div>${trafficBadge('warn','H1 múltiple')} <strong>${fmt(multiH1)}</strong></div><div>${trafficBadge('warn','H1 duplicado')} <strong>${fmt(dupH1)}</strong></div></div>`)}${panel('Problemas de Title y Meta Description', `<div class='sev-grid'><div>${trafficBadge('warn','Title corto')} <strong>${fmt(missT)}</strong></div><div>${trafficBadge('warn','Title largo')} <strong>${fmt(longT)}</strong></div><div>${trafficBadge('warn','Meta corta')} <strong>${fmt(missD)}</strong></div><div>${trafficBadge('warn','Meta larga')} <strong>${fmt(longD)}</strong></div></div>`)}
    ${panel('SEO Score',`<div class='total-card'><strong class='${scoreTone(score)}'>${score}%</strong><span>Estado SEO de corrida</span></div>`)}
    ${panel('Registro de URLs auditadas',`${moduleFiltersUI('seo')}${table(filteredRows,['page_url','has_title','has_meta_description','h1_count','has_canonical','has_noindex','has_lang','images_without_alt'],'seo')}`)}${panel('Hallazgos SEO', findingsTable(findings,'seo-findings'))}</div>
    <aside class='detail-drawer'>${panel('Detalle SEO',sel?detailSeo(sel,findings):`<div class='empty-box'>Selecciona una URL.</div>`,sel?`<button class='button' id='closeDetailSeo'>Cerrar</button>`:'')}</aside></div></div>`;
  bindDetailButtons(rows,'seo'); document.getElementById('closeDetailSeo')?.addEventListener('click',()=>{state.selectedByModule.seo=null; render();});
  bindModuleFilters("seo");
}

function detailSeo(r,findings){ return `<div class='detail-card'>${summaryLine('URL',`<a class='detail-url' target='_blank' href='${safe(r.page_url,'#')}'>${safe(r.page_url)}</a>`)}${summaryLine('Title',boolIcon(r.has_title))}${summaryLine('Meta description',boolIcon(r.has_meta_description))}${summaryLine('H1',fmt(r.h1_count))}${summaryLine('Canonical',boolIcon(r.has_canonical))}${summaryLine('Noindex',boolIcon(r.has_noindex))}${summaryLine('Idioma',boolIcon(r.has_lang))}${summaryLine('Imágenes sin ALT',fmt(r.images_without_alt))}<h3>Recomendaciones</h3>${recommendationsFor(r.page_url,findings)}</div>`; }

async function renderTagging(){
  const latest=await apiGet(moduleConfig.tagging.latest,null); if(!latest?.run_id) return app.innerHTML=`<div class='empty-box'>No hay corridas de tagging.</div>`;
  setRunChip(parseRunDate(latest));
  const rows=await apiGet(moduleConfig.tagging.results(latest.run_id),[]); const findings=await apiGet(moduleConfig.tagging.findings(latest.run_id),[]);
  const filteredRows = applyModuleFilters(rows, "tagging");
  const dbl=count(rows,r=>r.double_tagging_detected), score=taggingScore(rows); const sel=rows.find(r=>r.page_url===state.selectedByModule.tagging)||filteredRows[0];
  app.innerHTML=`<div class='page'>${pageHeader(moduleConfig.tagging.title,moduleConfig.tagging.subtitle)}<div class='module-layout technical-layout'><div class='main-column'>
    <div class='kpi-grid tagging-kpis'>${kpiCard({title:'GTM detectado',value:pct(rows,'has_gtm'),iconName:'new_releases',tone:'success'})}${kpiCard({title:'GA4 detectado',value:pct(rows,'has_ga4'),iconName:'analytics',tone:'success'})}${kpiCard({title:'dataLayer detectado',value:pct(rows,'has_datalayer'),iconName:'database',tone:'warning'})}${kpiCard({title:'Doble etiquetado',value:fmt(dbl),iconName:'error',tone:dbl?'danger':'success'})}</div>
    ${panel('Tagging Score',`<div class='total-card'><strong class='${scoreTone(score)}'>${score}%</strong><span>Estado de implementación</span></div>`)}
    ${panel('Análisis detallado por URL',`${moduleFiltersUI('tagging')}${table(filteredRows,['page_url','has_gtm','has_ga4','has_datalayer','cta_elements_count','form_elements_count','has_interactions','has_generate_lead_hint','has_whatsapp_click_hint','double_tagging_detected'],'tagging')}`)}${panel('Hallazgos Tagging', findingsTable(findings,'tag-findings'))}</div>
    <aside class='detail-drawer'>${panel('Detalle Tagging',sel?detailTag(sel,findings):`<div class='empty-box'>Selecciona una URL.</div>`,sel?`<button class='button' id='closeDetailTag'>Cerrar</button>`:'')}</aside></div></div>`;
  bindDetailButtons(rows,'tagging'); document.getElementById('closeDetailTag')?.addEventListener('click',()=>{state.selectedByModule.tagging=null; render();});
  bindModuleFilters("tagging");
}
function detailTag(r,findings){ return `<div class='detail-card'>${summaryLine('URL',`<a class='detail-url' target='_blank' href='${safe(r.page_url,'#')}'>${safe(r.page_url)}</a>`)}${summaryLine('GTM',boolIcon(r.has_gtm))}${summaryLine('GA4',boolIcon(r.has_ga4))}${summaryLine('dataLayer',boolIcon(r.has_datalayer))}${summaryLine('CTAs',fmt(r.cta_elements_count))}${summaryLine('Formularios',fmt(r.form_elements_count))}${summaryLine('Interacciones',boolIcon(r.has_interactions))}${summaryLine('Lead',boolIcon(r.has_generate_lead_hint))}${summaryLine('WhatsApp',boolIcon(r.has_whatsapp_click_hint))}${summaryLine('Doble etiquetado',boolIcon(r.double_tagging_detected))}<h3>Recomendaciones</h3>${recommendationsFor(r.page_url,findings)}</div>`; }

function summaryLine(label,value){ return `<div class='summary-line'><span>${label}</span><strong>${value}</strong></div>`; }

render();