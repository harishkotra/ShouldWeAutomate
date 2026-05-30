let currentResults = null;
let chartInstance = null;
let isMultiProcess = false;
let currentTab = "overview";
let llmAvailable = false;

document.addEventListener("DOMContentLoaded", async () => {
  await loadDimensions();
  await loadRoiFields();
  await loadBenchmarkStats();
  await loadBenchmark();
  await checkLlmStatus();
});

/* === TIER / GAMIFICATION HELPERS === */

function getTier(score) {
  if (score >= 85)
    return {
      text: "Mythic",
      icon: "🏆",
      cls: "tier-excellent",
      color: "#3b82f6",
    };
  if (score >= 70)
    return { text: "Gold", icon: "🥇", cls: "tier-good", color: "#22c55e" };
  if (score >= 50)
    return {
      text: "Silver",
      icon: "🥈",
      cls: "tier-moderate",
      color: "#eab308",
    };
  if (score >= 30)
    return { text: "Bronze", icon: "🥉", cls: "tier-poor", color: "#f97316" };
  return {
    text: "Critical",
    icon: "⛔",
    cls: "tier-critical",
    color: "#ef4444",
  };
}

function getRecData(score) {
  if (score < 30) return { level: "DO NOT AUTOMATE", color: "#ef4444" };
  if (score < 50) return { level: "IMPROVE PROCESS FIRST", color: "#f97316" };
  if (score < 70) return { level: "HUMAN-IN-THE-LOOP AI", color: "#eab308" };
  if (score < 85) return { level: "AI ASSISTED AUTOMATION", color: "#22c55e" };
  return { level: "AGENT AUTOMATION READY", color: "#3b82f6" };
}

/* === DIMENSION SCORING — GAMIFIED === */

async function loadDimensions() {
  const res = await fetch("/api/dimensions");
  const dims = await res.json();
  window.__dimensionsCache = dims;

  document.getElementById("dimension-forms").innerHTML = "";
  const dimKeys = Object.keys(dims);
  dimKeys.forEach((key) => {
    const section = createDimSection(key, dims[key], "");
    document.getElementById("dimension-forms").appendChild(section);
  });

  const spContainer = document.querySelector(
    "#sub-processes-container .sub-process .dim-questions",
  );
  if (spContainer) {
    spContainer.innerHTML = "";
    dimKeys.forEach((key) => {
      const section = createDimSection(key, dims[key], "sp0_");
      spContainer.appendChild(section);
    });
  }

  updateLivePreview();
}

function createDimSection(key, dim, prefix) {
  const section = document.createElement("div");
  section.className = "dim-section";

  const aggDefault = Math.round(
    dim.questions.reduce((s, q) => s + q.default, 0) / dim.questions.length,
  );
  const tier = getTier(aggDefault);

  section.innerHTML = `
    <div class="dim-header" onclick="toggleDim(this)">
      <h3>${dim.label}</h3>
      <div class="dim-meta">
        <span class="tier-badge ${tier.cls}" id="tier-${prefix}${key}">${tier.icon} ${tier.text}</span>
        <span style="font-size:12px;color:var(--text-muted)">${dim.weight * 100}%</span>
        <span class="fine-tune-toggle" onclick="event.stopPropagation();toggleFineTune('${prefix}${key}')">⚙️ Fine-tune</span>
      </div>
    </div>
    <div class="form-group" style="margin-bottom:4px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <label class="form-label" style="margin-bottom:0;font-size:13px">Overall ${dim.label}</label>
        <span class="score-display" id="display-agg-${prefix}${key}" style="font-size:20px;font-weight:700">${aggDefault}</span>
      </div>
      <input type="range" id="input-agg-${prefix}${key}" min="0" max="100" value="${aggDefault}"
        oninput="updateAggregate('${prefix}', '${key}')">
    </div>
    <div class="sub-sliders" id="sub-${prefix}${key}">
      ${dim.questions
        .map(
          (q) => `
        <div class="sub-slider-group">
          <label class="form-label">
            <span>${q.text}</span>
            <span class="score-display" id="display-${prefix}${q.id}">${q.default}</span>
          </label>
          <input type="range" id="input-${prefix}${q.id}" min="${q.min}" max="${q.max}" value="${q.default}"
            oninput="updateSubSlider('${prefix}', '${key}', '${q.id}')">
        </div>
      `,
        )
        .join("")}
    </div>
  `;
  return section;
}

function toggleDim(header) {
  const section = header.closest(".dim-section");
  const body = section.querySelector(".form-group");
  const sub = section.querySelector(".sub-sliders");
  if (!body) return;
  const wasHidden = body.style.display === "none";
  body.style.display = wasHidden ? "" : "none";
  if (sub) {
    sub.style.display = wasHidden
      ? sub.classList.contains("open")
        ? "block"
        : "none"
      : "none";
  }
}

function toggleFineTune(prefixKey) {
  const container = document.getElementById(`sub-${prefixKey}`);
  if (!container) return;
  const isOpen = container.classList.toggle("open");
  container.style.display = isOpen ? "block" : "none";
  const btn = container
    .closest(".dim-section")
    ?.querySelector(".fine-tune-toggle");
  if (btn) btn.classList.toggle("active", isOpen);
  const mainSlider = container
    .closest(".dim-section")
    ?.querySelector(".form-group");
  if (mainSlider) mainSlider.style.display = "block";
}

function updateAggregate(prefix, key) {
  const aggInput = document.getElementById(`input-agg-${prefix}${key}`);
  const aggDisplay = document.getElementById(`display-agg-${prefix}${key}`);
  const val = parseInt(aggInput.value) || 50;
  if (aggDisplay) aggDisplay.textContent = val;

  const dimRes = window.__dimensionsCache || {};
  if (!window.__dimensionsCache) return;

  const dim = window.__dimensionsCache[key];
  if (!dim) return;

  dim.questions.forEach((q) => {
    const subInput = document.getElementById(`input-${prefix}${q.id}`);
    const subDisplay = document.getElementById(`display-${prefix}${q.id}`);
    if (subInput) subInput.value = val;
    if (subDisplay) subDisplay.textContent = val;
  });

  updateDimTier(prefix, key, val);
  updateLivePreview();
}

function updateSubSlider(prefix, key, qId) {
  const subInput = document.getElementById(`input-${prefix}${qId}`);
  const subDisplay = document.getElementById(`display-${prefix}${qId}`);
  if (subDisplay) subDisplay.textContent = subInput.value;

  const dim = window.__dimensionsCache && window.__dimensionsCache[key];
  if (!dim) return;

  let sum = 0,
    count = 0;
  dim.questions.forEach((q) => {
    const el = document.getElementById(`input-${prefix}${q.id}`);
    if (el) {
      sum += parseInt(el.value) || 0;
      count++;
    }
  });
  const avg = count > 0 ? Math.round(sum / count) : 50;

  const aggInput = document.getElementById(`input-agg-${prefix}${key}`);
  const aggDisplay = document.getElementById(`display-agg-${prefix}${key}`);
  if (aggInput) aggInput.value = avg;
  if (aggDisplay) aggDisplay.textContent = avg;

  updateDimTier(prefix, key, avg);
  updateLivePreview();
}

function updateDimTier(prefix, key, val) {
  const badge = document.getElementById(`tier-${prefix}${key}`);
  if (!badge) return;
  const tier = getTier(val);
  badge.className = `tier-badge ${tier.cls}`;
  badge.innerHTML = `${tier.icon} ${tier.text}`;
}

/* === LIVE PREVIEW === */

function updateLivePreview() {
  const dimKeys = [
    "data_quality",
    "process_stability",
    "exception_rate",
    "decision_complexity",
    "integration_readiness",
    "governance_risk",
    "roi_potential",
  ];
  const weights = [0.2, 0.2, 0.15, 0.15, 0.1, 0.1, 0.1];

  let total = 0;
  dimKeys.forEach((key, i) => {
    const aggDisplay = document.getElementById(`display-agg-${key}`);
    const val = aggDisplay ? parseInt(aggDisplay.textContent) || 50 : 50;
    total += val * weights[i];
  });
  const overall = Math.round(total);

  const gauge = document.getElementById("live-gauge");
  const score = document.getElementById("live-score");
  const rec = document.getElementById("live-rec");
  const badge = document.getElementById("live-tier-badge");
  const conf = document.getElementById("live-confidence");

  if (gauge) {
    const circ = 2 * Math.PI * 34;
    const offset = circ - (overall / 100) * circ;
    gauge.style.strokeDasharray = circ;
    gauge.style.strokeDashoffset = offset;
    const recData = getRecData(overall);
    gauge.style.stroke = recData.color;
  }
  if (score) {
    score.textContent = overall;
    const recData = getRecData(overall);
    score.style.color = recData.color;
  }
  if (rec) {
    const recData = getRecData(overall);
    rec.innerHTML = `<span style="color:${recData.color};font-weight:700">${recData.level}</span> — Based on your current scores`;
  }
  if (badge) {
    const tier = getTier(overall);
    badge.className = `tier-badge ${tier.cls}`;
    badge.innerHTML = `${tier.icon} ${tier.text} · ${overall}/100`;
  }
  if (conf) {
    conf.textContent =
      overall < 50 ? "🔄 Focus on improving lower dimensions first" : "";
  }

  const tooltip = document.getElementById("live-preview-tooltip");
  if (tooltip) {
    const recData = getRecData(overall);
    tooltip.querySelector("#tooltip-score").textContent = overall;
    tooltip.querySelector("#tooltip-score").style.color = recData.color;
    tooltip.querySelector("#tooltip-rec").textContent = recData.level;
    tooltip.style.display = "block";
  }
}

/* === SUB-PROCESS DECOMPOSITION === */

let subProcessCount = 1;

function addSubProcess() {
  if (!isMultiProcess) return;
  const idx = subProcessCount++;
  const container = document.getElementById("sub-processes-container");
  const div = document.createElement("div");
  div.className = "sub-process";
  div.dataset.index = idx;
  div.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:8px">
      <input type="text" class="sp-name filter-input" value="Sub-Process ${idx}" placeholder="Sub-process name" style="width:50%">
      <div style="display:flex;align-items:center;gap:8px">
        <label style="font-size:12px;color:var(--text-muted)">Weight:</label>
        <input type="number" class="sp-weight filter-input" value="1" min="0.1" max="10" step="0.1" style="width:70px">
      </div>
      <button class="btn btn-danger" style="padding:4px 12px;font-size:12px" onclick="removeSubProcess(this)">✕</button>
    </div>
    <div class="dim-questions"></div>
  `;
  container.appendChild(div);

  fetch("/api/dimensions")
    .then((r) => r.json())
    .then((dims) => {
      const qContainer = div.querySelector(".dim-questions");
      window.__dimensionsCache = dims;
      Object.keys(dims).forEach((key) => {
        const section = createDimSection(key, dims[key], `sp${idx}_`);
        qContainer.appendChild(section);
      });
    });
}

function removeSubProcess(btn) {
  if (document.querySelectorAll(".sub-process").length <= 1) return;
  btn.closest(".sub-process").remove();
}

function toggleSubProcessMode() {
  isMultiProcess = !isMultiProcess;
  document.getElementById("sp-toggle").textContent = isMultiProcess
    ? "Single Process Mode"
    : "Multi-Process Mode";
  document.querySelectorAll(".sub-process:not(:first-child)").forEach((el) => {
    el.style.display = isMultiProcess ? "" : "none";
  });
  if (isMultiProcess && subProcessCount === 1) addSubProcess();
  document.getElementById("sp-help-text").textContent = isMultiProcess
    ? "⚡ Multi-process mode: each sub-process gets its own scores. Aggregate scores are weighted by sub-process weight."
    : "ℹ️ Single process mode: one set of scores for the entire workflow.";
}

/* === ROI CALCULATOR === */

async function loadRoiFields() {
  const res = await fetch("/api/roi/fields");
  const fields = await res.json();
  const container = document.getElementById("roi-fields");
  container.innerHTML = fields
    .map((f) => {
      const prefix = f.prefix
        ? `<span style="color:var(--text-muted);margin-right:4px">${f.prefix}</span>`
        : "";
      const suffix = f.suffix
        ? `<span style="color:var(--text-muted);margin-left:4px">${f.suffix}</span>`
        : "";
      return `
        <div class="form-group" style="display:flex;align-items:center;gap:12px">
          <label class="form-label" style="flex:1;margin:0">${f.label}</label>
          <div style="display:flex;align-items:center;width:200px">
            ${prefix}
            <input type="${f.type}" id="roi-${f.id}" class="filter-input" value="${f.default}" style="width:100px;text-align:right">
            ${suffix}
          </div>
        </div>
      `;
    })
    .join("");
}

function toggleRoiCalculator() {
  const el = document.getElementById("roi-calculator");
  el.style.display = el.style.display === "none" ? "block" : "none";
  document.getElementById("roi-toggle").textContent =
    el.style.display === "none" ? "Show ROI Calculator" : "Hide ROI Calculator";
}

function collectRoiParams() {
  const fields = [
    "headcount",
    "avg_annual_salary",
    "annual_volume",
    "hours_per_unit_current",
    "hours_per_unit_automated",
    "error_rate_current_pct",
    "error_rate_automated_pct",
    "avg_cost_per_error",
    "automation_budget",
  ];
  const params = {};
  fields.forEach((f) => {
    const el = document.getElementById(`roi-${f}`);
    if (el) params[f] = parseFloat(el.value) || 0;
  });
  params.maintenance_yearly = params.automation_budget * 0.15;
  return params;
}

/* === COLLECT ALL RESPONSES === */

function collectResponses() {
  const responses = {};
  responses["workflow_name"] =
    document.getElementById("wf-name").value || "Unnamed Workflow";
  responses["industry"] =
    document.getElementById("wf-industry").value || "Unknown";
  responses["description"] = document.getElementById("wf-desc").value || "";

  document
    .querySelectorAll('#dimension-forms input[type="range"]')
    .forEach((input) => {
      const id = input.id;
      if (id.startsWith("input-agg-")) return;
      const qId = id.replace("input-", "");
      responses[qId] = parseInt(input.value);
    });

  if (isMultiProcess) {
    const spContainers = document.querySelectorAll(
      "#sub-processes-container .sub-process",
    );
    const subProcesses = [];
    spContainers.forEach((sp) => {
      const name = sp.querySelector(".sp-name")?.value || "Unnamed";
      const weight = parseFloat(sp.querySelector(".sp-weight")?.value || "1");
      const spResponses = {};
      sp.querySelectorAll('input[type="range"]').forEach((input) => {
        const id = input.id;
        if (id.startsWith("input-agg-")) return;
        const qId = id.replace(/input-sp\d+_/, "");
        spResponses[qId] = parseInt(input.value);
      });
      subProcesses.push({
        name,
        weight,
        description: "",
        responses: spResponses,
      });
    });
    if (subProcesses.length > 1) responses["sub_processes"] = subProcesses;
  }

  responses["roi_params"] = collectRoiParams();

  const useLlmCheckbox = document.getElementById("use-llm");
  responses["use_llm"] =
    useLlmCheckbox && useLlmCheckbox.checked && llmAvailable;

  return responses;
}

/* === ANALYSIS === */

async function analyzeWorkflow() {
  const btn = document.getElementById("analyze-btn");
  btn.disabled = true;
  btn.innerHTML = "⏳ Analyzing across all dimensions...";

  const responses = collectResponses();

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(responses),
    });
    const result = await res.json();
    currentResults = result;
    renderResults(result);
  } catch (e) {
    alert("Analysis failed. Is the server running?");
    console.error(e);
  }

  btn.disabled = false;
  btn.innerHTML = "⚡ Analyze Workflow";
}

function resetAnalysis() {
  document.getElementById("results-area").style.display = "none";
  document.getElementById("form-area").style.display = "block";
  document.getElementById("live-preview-tooltip").style.display = "none";
  document
    .getElementById("results-area")
    .scrollIntoView({ behavior: "smooth" });
}

/* === RESULTS RENDERING === */

function switchResultsTab(tab, btn) {
  currentTab = tab;
  document
    .querySelectorAll("#results-tabs .tab")
    .forEach((t) => t.classList.remove("active"));
  document
    .querySelectorAll(".tab-content")
    .forEach((t) => (t.style.display = "none"));
  btn.classList.add("active");
  const el = document.getElementById(`tab-${tab}`);
  if (el) {
    el.style.display = "block";
    if (tab === "whatif") renderWhatIfTab();
    if (tab === "explanation") renderExplanationTab();
    if (tab === "remediation") renderRemediationTab();
    if (tab === "regulatory") renderRegulatoryTab();
    if (tab === "ai") renderAiTab();
  }
}

function renderResults(r) {
  document.getElementById("form-area").style.display = "none";
  const container = document.getElementById("results-content");
  const rec = r.recommendation;
  const dims = r.dimension_scores;
  const gaugeColor =
    r.overall_score >= 85
      ? "#22c55e"
      : r.overall_score >= 70
        ? "#3b82f6"
        : r.overall_score >= 50
          ? "#eab308"
          : r.overall_score >= 30
            ? "#f97316"
            : "#ef4444";
  const gaugeCirc = 2 * Math.PI * 90;

  const dimLabels = {
    data_quality: "Data Quality",
    process_stability: "Process Stability",
    exception_rate: "Exception Rate",
    decision_complexity: "Decision Complexity",
    integration_readiness: "Tool Integration",
    governance_risk: "Governance Risk",
    roi_potential: "ROI Potential",
  };

  const hasROI = r.roi_estimate && r.roi_estimate.quantitative;

  container.innerHTML = `
    <div class="card" style="text-align:center;padding:32px">
      <h2 style="margin-bottom:4px">${document.getElementById("wf-name").value || "Workflow Analysis"}</h2>
      <p style="color:var(--text-secondary);margin-bottom:24px">${document.getElementById("wf-industry").value || ""} ${document.getElementById("wf-desc").value ? "— " + document.getElementById("wf-desc").value : ""}</p>
      <div class="gauge-container">
        <div class="gauge">
          <svg width="200" height="200" viewBox="0 0 200 200">
            <circle class="gauge-bg" cx="100" cy="100" r="90"/>
            <circle class="gauge-value" cx="100" cy="100" r="90" stroke="${gaugeColor}"
              stroke-dasharray="${gaugeCirc}" stroke-dashoffset="${gaugeCirc - (r.overall_score / 100) * gaugeCirc}"/>
          </svg>
          <div class="gauge-text"><div class="score" style="color:${gaugeColor}">${r.overall_score}</div><div class="label">Overall Readiness</div></div>
        </div>
      </div>
      <div class="recommendation-badge" style="background:${rec.color}20;color:${rec.color};border:1px solid ${rec.color}40">
        ${r.overall_score >= 85 ? "🚀" : r.overall_score >= 70 ? "⚡" : r.overall_score >= 50 ? "🔶" : r.overall_score >= 30 ? "⚠️" : "🛑"} ${rec.level}
      </div>
      <p style="color:var(--text-secondary);max-width:600px;margin:12px auto">${rec.reason}</p>
      <p style="font-size:13px;color:var(--text-muted)">Confidence: ${r.confidence}% · ${r.architecture.type} · ${r.sub_processes.count} sub-process(es)</p>
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <div class="card-title">Dimension Scores</div>
        <div class="scores-grid">
          ${Object.entries(dimLabels)
            .map(([key, label]) => {
              const val = dims[key] || 0;
              const color =
                val >= 70
                  ? "#22c55e"
                  : val >= 50
                    ? "#eab308"
                    : val >= 30
                      ? "#f97316"
                      : "#ef4444";
              return `<div class="score-card"><div class="value" style="color:${color}">${val}</div><div class="dim-label">${label}</div></div>`;
            })
            .join("")}
        </div>
      </div>
      <div class="card">
        <div class="card-title">Radar View</div>
        <div class="chart-container"><canvas id="radarChart"></canvas></div>
      </div>
    </div>
  `;

  renderRadarChart(r.radar_values);
  renderOverviewTab(r);
  renderExplanationTab();
  renderWhatIfTab();
  renderRemediationTab();
  renderRegulatoryTab();

  const aiBtn = document.getElementById("tab-ai-btn");
  if (r.llm_enriched && aiBtn) {
    aiBtn.style.display = "inline-block";
    renderAiTab();
  } else if (aiBtn) {
    aiBtn.style.display = "none";
  }

  document.getElementById("results-area").style.display = "block";
  document
    .getElementById("results-area")
    .scrollIntoView({ behavior: "smooth" });
}

function renderOverviewTab(r) {
  const container = document.getElementById("tab-overview");
  container.innerHTML = `
    <div class="dashboard-grid">
      <div>
        <h3 style="margin-bottom:12px">Risks</h3>
        ${
          r.top_risks.length > 0
            ? r.top_risks
                .map(
                  (risk) => `
          <div class="risk-item ${risk.severity.toLowerCase()}">
            <strong style="font-size:14px">${risk.severity}</strong>
            <p style="font-size:13px;margin:4px 0;color:var(--text-secondary)">${risk.risk}</p>
            <p style="font-size:12px;color:var(--text-muted)">→ ${risk.mitigation}</p>
          </div>
        `,
                )
                .join("")
            : '<p style="color:var(--text-secondary)">No significant risks detected.</p>'
        }
      </div>
      <div>
        <h3 style="margin-bottom:12px">Red Flags</h3>
        ${
          r.red_flags.length > 0
            ? r.red_flags
                .map(
                  (flag) => `
          <div class="risk-item" style="border-left-color:var(--accent-red)">
            <p style="font-size:13px;color:var(--accent-red)">${flag}</p>
          </div>
        `,
                )
                .join("")
            : '<p style="color:var(--text-secondary)">No red flags detected.</p>'
        }
      </div>
    </div>

    <h3 style="margin:24px 0 12px">Failure Mode Analysis</h3>
    <div class="failure-grid">
      ${r.failure_modes
        .map((fm) => {
          const sevClass =
            fm.severity.toLowerCase() === "critical"
              ? "severity-critical"
              : fm.severity.toLowerCase() === "high"
                ? "severity-high"
                : fm.severity.toLowerCase() === "medium"
                  ? "severity-medium"
                  : "severity-low";
          return `<div class="failure-card">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px">
            <strong style="font-size:14px">${fm.mode}</strong>
            <span class="failure-severity ${sevClass}">${fm.severity}</span>
          </div>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${fm.description}</p>
          <div style="display:flex;gap:12px;font-size:12px;color:var(--text-muted)">
            <span>Likelihood: ${fm.likelihood}</span>
            <span>Detectability: ${fm.detectability}</span>
          </div>
        </div>`;
        })
        .join("")}
    </div>

    <div class="dashboard-grid" style="margin-top:24px">
      <div>
        <h3 style="margin-bottom:12px">ROI Estimate</h3>
        ${
          r.roi_estimate.quantitative
            ? `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div class="score-card"><div style="font-size:14px;font-weight:600;color:${r.roi_estimate.quantitative.classification.color}">${r.roi_estimate.quantitative.classification.category}</div><div class="dim-label">Category</div></div>
            <div class="score-card"><div style="font-size:18px;font-weight:600;color:var(--accent-green)">$${r.roi_estimate.quantitative.annual_savings.toLocaleString()}</div><div class="dim-label">Annual Savings</div></div>
            <div class="score-card"><div style="font-size:18px;font-weight:600">${r.roi_estimate.quantitative.payback_years ? r.roi_estimate.quantitative.payback_years + " yrs" : "N/A"}</div><div class="dim-label">Payback Period</div></div>
            <div class="score-card"><div style="font-size:18px;font-weight:600;color:var(--accent-blue)">${r.roi_estimate.quantitative.roi_3yr_pct}%</div><div class="dim-label">3-Year ROI</div></div>
            <div class="score-card"><div style="font-size:18px;font-weight:600">$${r.roi_estimate.quantitative.npv_3yr.toLocaleString()}</div><div class="dim-label">3-Year NPV</div></div>
            <div class="score-card"><div style="font-size:18px;font-weight:600">${r.roi_estimate.quantitative.ftes_redeployed} FTEs</div><div class="dim-label">Redeployed</div></div>
          </div>
        `
            : `
          <div class="scores-grid" style="grid-template-columns:1fr 1fr">
            <div class="score-card"><div style="font-size:16px;font-weight:600">${r.roi_estimate.category}</div><div class="dim-label">Category</div></div>
            <div class="score-card"><div style="font-size:14px;color:var(--text-secondary)">${r.roi_estimate.time_saved}</div><div class="dim-label">Time Saved</div></div>
            <div class="score-card"><div style="font-size:14px;color:var(--text-secondary)">${r.roi_estimate.cost_reduction}</div><div class="dim-label">Cost Reduction</div></div>
            <div class="score-card"><div style="font-size:14px;color:var(--text-secondary)">${r.roi_estimate.payback_period}</div><div class="dim-label">Payback</div></div>
          </div>
          <p style="font-size:12px;color:var(--text-muted);margin-top:8px">Enable the ROI Calculator in the form for quantitative projections.</p>
        `
        }
      </div>
      <div>
        <h3 style="margin-bottom:12px">Implementation</h3>
        <div class="scores-grid" style="grid-template-columns:1fr 1fr">
          <div class="score-card"><div style="font-size:16px;font-weight:600">${r.implementation.effort}</div><div class="dim-label">Effort</div></div>
          <div class="score-card"><div style="font-size:16px;font-weight:600;color:var(--accent-yellow)">${r.implementation.timeline}</div><div class="dim-label">Timeline</div></div>
          <div class="score-card"><div style="font-size:13px;color:var(--text-secondary)">${r.implementation.maintenance_cost}</div><div class="dim-label">Maintenance</div></div>
          <div class="score-card"><div style="font-size:13px;color:var(--text-secondary)">${r.implementation.human_oversight}</div><div class="dim-label">Oversight</div></div>
        </div>
        <p style="font-size:13px;color:var(--text-secondary);margin-top:8px"><strong>Architecture:</strong> ${r.architecture.type}</p>
        <p style="font-size:12px;color:var(--text-secondary)">${r.architecture.description}</p>
        ${r.architecture.components.length > 0 ? `<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">${r.architecture.components.map((c) => `<span class="tag tag-info">${c}</span>`).join("")}</div>` : ""}
      </div>
    </div>

    <h3 style="margin:24px 0 12px">Sub-Process Decomposition</h3>
    <div class="scores-grid" style="grid-template-columns:repeat(auto-fill,minmax(200px,1fr))">
      ${Object.entries(r.sub_processes.decomposition || {})
        .map(([name, scores]) => {
          const overall = Object.entries(scores).reduce((sum, [k, v]) => {
            const weights = {
              data_quality: 0.2,
              process_stability: 0.2,
              exception_rate: 0.15,
              decision_complexity: 0.15,
              integration_readiness: 0.1,
              governance_risk: 0.1,
              roi_potential: 0.1,
            };
            return sum + v * (weights[k] || 0);
          }, 0);
          return `<div class="score-card"><div style="font-size:16px;font-weight:600;color:${overall >= 70 ? "#22c55e" : overall >= 50 ? "#eab308" : "#f97316"}">${Math.round(overall)}</div><div class="dim-label">${name}</div></div>`;
        })
        .join("")}
    </div>

    <h3 style="margin:24px 0 12px">Benchmark Similar Workflows</h3>
    ${
      r.benchmark_similar && r.benchmark_similar.length > 0
        ? `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">
        ${r.benchmark_similar
          .map(
            (b) => `
          <div class="compare-item">
            <div class="name">${b.workflow_name}</div>
            <div class="industry">${b.industry} · Score: ${b.overall_score} · Similarity: ${b.similarity}%</div>
            <span class="tag" style="background:${b.category === "AGENT AUTOMATION READY" ? "rgba(34,197,94,0.15)" : "rgba(234,179,8,0.15)"};color:${b.category === "AGENT AUTOMATION READY" ? "#22c55e" : "#eab308"}">${b.category}</span>
          </div>
        `,
          )
          .join("")}
      </div>
    `
        : '<p style="color:var(--text-muted);font-size:13px">No similar benchmark workflows found for this configuration.</p>'
    }

    <h3 style="margin:24px 0 12px">Next Steps</h3>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      ${r.next_steps
        .map(
          (step, i) => `
        <div style="flex:1;min-width:200px;padding:12px;background:var(--bg-input);border-radius:8px;display:flex;align-items:start;gap:8px">
          <span style="background:var(--accent-blue);color:white;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;flex-shrink:0">${i + 1}</span>
          <span style="font-size:13px">${step}</span>
        </div>
      `,
        )
        .join("")}
    </div>
  `;
}

function renderRadarChart(values) {
  if (chartInstance) chartInstance.destroy();
  const ctx = document.getElementById("radarChart");
  if (!ctx) return;
  const labels = Object.keys(values);
  const data = Object.values(values);
  chartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: [
        {
          label: "Readiness",
          data,
          backgroundColor: "rgba(59,130,246,0.15)",
          borderColor: "rgba(59,130,246,0.8)",
          borderWidth: 2,
          pointBackgroundColor: data.map((v) =>
            v >= 70
              ? "#22c55e"
              : v >= 50
                ? "#eab308"
                : v >= 30
                  ? "#f97316"
                  : "#ef4444",
          ),
          pointBorderColor: "#1a1d27",
          pointBorderWidth: 2,
          pointRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20,
            color: "#6b7280",
            backdropColor: "transparent",
            font: { size: 10 },
          },
          grid: { color: "rgba(51,56,80,0.5)" },
          angleLines: { color: "rgba(51,56,80,0.5)" },
          pointLabels: { color: "#9aa0b0", font: { size: 11, weight: "500" } },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
}

/* === EXPLANATION TAB === */

async function renderExplanationTab() {
  if (!currentResults) return;
  const container = document.getElementById("tab-explanation");
  const r = currentResults;
  const dims = r.dimension_scores;

  const responses = {};
  document
    .querySelectorAll('#dimension-forms input[type="range"]')
    .forEach((input) => {
      const id = input.id;
      if (id.startsWith("input-agg-")) return;
      const qId = id.replace("input-", "");
      responses[qId] = parseInt(input.value);
    });

  let explanation;
  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dimension_scores: dims, responses }),
    });
    explanation = await res.json();
  } catch (e) {
    container.innerHTML =
      '<p style="color:var(--text-muted)">Explanation data unavailable.</p>';
    return;
  }

  const dimLabels = {
    data_quality: "Data Quality",
    process_stability: "Process Stability",
    exception_rate: "Exception Rate",
    decision_complexity: "Decision Complexity",
    integration_readiness: "Tool Integration",
    governance_risk: "Governance Risk",
    roi_potential: "ROI Potential",
  };

  container.innerHTML = `
    <h3 style="margin-bottom:16px">Score Breakdown</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      ${Object.entries(dimLabels)
        .map(([key, label]) => {
          const exp = explanation.explanations?.[key];
          if (!exp) return "";
          const up = exp.pulling_up || [];
          const down = exp.pulling_down || [];
          return `<div style="background:var(--bg-input);border-radius:10px;padding:16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <strong>${label}</strong>
            <span style="font-size:24px;font-weight:700;color:${exp.score >= 70 ? "#22c55e" : exp.score >= 50 ? "#eab308" : "#ef4444"}">${exp.score}</span>
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px">
            Weight: ${exp.weight * 100}% · Contribution: ${exp.weighted_contribution} pts · ${exp.verdict}
          </div>
          ${up.length > 0 ? `<div style="margin:6px 0;font-size:12px;color:var(--accent-green)">▲ Pulling up: ${up.map((u) => u.text).join(", ")}</div>` : ""}
          ${down.length > 0 ? `<div style="margin:6px 0;font-size:12px;color:var(--accent-red)">▼ Pulling down: ${down.map((d) => d.text).join(", ")}</div>` : ""}
          <div style="margin-top:8px;padding:8px;background:var(--bg-card);border-radius:6px;font-size:12px;color:var(--accent-blue)">
            💡 ${exp.improvement_tip}
          </div>
        </div>`;
        })
        .join("")}
    </div>

    ${
      explanation.suggestions && explanation.suggestions.length > 0
        ? `
      <h3 style="margin:24px 0 12px">Priority Improvements</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        ${explanation.suggestions
          .map(
            (s) => `
          <div style="background:var(--bg-input);border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center">
            <div><strong style="font-size:13px">${s.dimension}</strong><div style="font-size:11px;color:var(--text-muted)">${s.suggestion}</div></div>
            <span style="font-size:14px;font-weight:600;color:var(--accent-green)">+${s.potential_gain} pts</span>
          </div>
        `,
          )
          .join("")}
      </div>
    `
        : ""
    }

    <h3 style="margin:24px 0 12px">Strongest & Weakest Dimensions</h3>
    <div class="dashboard-grid">
      <div>
        <h4 style="font-size:13px;color:var(--accent-green);margin-bottom:8px">Strongest</h4>
        ${
          explanation.score_summary?.strongest_dimensions
            ?.map(
              (d) =>
                `<div style="padding:8px;background:var(--bg-input);border-radius:6px;margin-bottom:4px;display:flex;justify-content:space-between">
            <span>${d.label}</span><span style="font-weight:600;color:var(--accent-green)">${d.score}</span>
          </div>`,
            )
            .join("") || ""
        }
      </div>
      <div>
        <h4 style="font-size:13px;color:var(--accent-red);margin-bottom:8px">Weakest</h4>
        ${
          explanation.score_summary?.weakest_dimensions
            ?.map(
              (d) =>
                `<div style="padding:8px;background:var(--bg-input);border-radius:6px;margin-bottom:4px;display:flex;justify-content:space-between">
            <span>${d.label}</span><span style="font-weight:600;color:var(--accent-red)">${d.score}</span>
          </div>`,
            )
            .join("") || ""
        }
      </div>
    </div>
    <p style="font-size:12px;color:var(--text-muted);margin-top:8px">Score spread: ${explanation.score_summary?.spread || 0} points</p>
  `;
}

/* === WHAT-IF TAB === */

async function renderWhatIfTab() {
  if (!currentResults) return;
  const container = document.getElementById("tab-whatif");
  const dims = currentResults.dimension_scores;

  let sensitivity, presets;
  try {
    const [sensRes, presetRes] = await Promise.all([
      fetch("/api/sensitivity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ base_scores: dims }),
      }).then((r) => r.json()),
      fetch("/api/what-if/presets").then((r) => r.json()),
    ]);
    sensitivity = sensRes;
    presets = presetRes;
  } catch (e) {
    container.innerHTML =
      '<p style="color:var(--text-muted)">What-if data unavailable.</p>';
    return;
  }

  const base = currentResults.overall_score;
  const dimLabels = {
    data_quality: "Data Quality",
    process_stability: "Process Stability",
    exception_rate: "Exception Rate",
    decision_complexity: "Decision Complexity",
    integration_readiness: "Tool Integration",
    governance_risk: "Governance Risk",
    roi_potential: "ROI Potential",
  };

  container.innerHTML = `
    <h3 style="margin-bottom:12px">Sensitivity Analysis</h3>
    <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">Base score: <strong>${base}</strong>. Each dimension's impact of +10 points on the overall score.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin-bottom:24px">
      ${sensitivity.ranked_dimensions
        ?.map((d) => {
          const barWidth = Math.max(5, (d.impact_per_10_pts / 2) * 100);
          return `<div style="background:var(--bg-input);border-radius:8px;padding:12px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:13px">${d.label}</span>
            <span style="font-size:13px;font-weight:600">+${d.impact_per_10_pts}</span>
          </div>
          <div style="height:6px;background:var(--bg-card);border-radius:3px;overflow:hidden">
            <div style="height:100%;width:${barWidth}%;background:linear-gradient(90deg,var(--accent-blue),var(--accent-purple));border-radius:3px"></div>
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px">Current: ${d.current_score} · Potential: ${d.improvement_potential} pts</div>
        </div>`;
        })
        .join("")}
    </div>

    <h3 style="margin-bottom:12px">Preset Scenarios</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px;margin-bottom:24px">
      ${presets
        .map(
          (p) => `
        <div class="card" style="padding:16px;cursor:pointer;margin:0" onclick="applyWhatIfPreset('${p.name}')">
          <strong style="font-size:14px">${p.name}</strong>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px">
            ${Object.entries(p.adjustments)
              .map(([k, v]) => `${dimLabels[k] || k}: +${v}`)
              .join(", ")}
          </div>
          <div style="margin-top:8px;font-size:12px;color:var(--accent-blue)">Click to simulate →</div>
        </div>
      `,
        )
        .join("")}
    </div>

    <div id="whatif-custom">
      <h3 style="margin-bottom:12px">Custom Adjustment</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px">
        ${Object.entries(dimLabels)
          .map(
            ([key, label]) => `
          <div style="display:flex;align-items:center;gap:8px">
            <label style="font-size:12px;flex:1;color:var(--text-secondary)">${label} (${dims[key]}):</label>
            <input type="range" id="wi-${key}" min="-50" max="50" value="0" style="flex:1"
              oninput="updateWhatIfPreview()">
            <span id="wi-val-${key}" style="font-size:12px;font-weight:600;width:35px;text-align:right;color:var(--accent-blue)">0</span>
          </div>
        `,
          )
          .join("")}
      </div>
      <div id="whatif-preview" style="margin-top:16px;padding:16px;background:var(--bg-input);border-radius:10px;text-align:center">
        <p style="font-size:13px;color:var(--text-muted)">Adjust sliders above to preview score changes</p>
      </div>
    </div>
  `;
}

let whatIfTimeout = null;

async function updateWhatIfPreview() {
  clearTimeout(whatIfTimeout);
  whatIfTimeout = setTimeout(async () => {
    if (!currentResults) return;
    const adjustments = {};
    Object.keys(currentResults.dimension_scores).forEach((key) => {
      const el = document.getElementById(`wi-${key}`);
      if (el) {
        const val = parseInt(el.value) || 0;
        adjustments[key] = val;
        const valEl = document.getElementById(`wi-val-${key}`);
        if (valEl) valEl.textContent = (val > 0 ? "+" : "") + val;
      }
    });

    try {
      const res = await fetch("/api/what-if", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          base_scores: currentResults.dimension_scores,
          adjustments,
        }),
      });
      const result = await res.json();
      const container = document.getElementById("whatif-preview");
      const color =
        result.overall_score >= 85
          ? "#22c55e"
          : result.overall_score >= 70
            ? "#3b82f6"
            : result.overall_score >= 50
              ? "#eab308"
              : result.overall_score >= 30
                ? "#f97316"
                : "#ef4444";
      container.innerHTML = `
        <div style="font-size:36px;font-weight:700;color:${color}">${result.overall_score}</div>
        <div style="font-size:13px;color:var(--text-muted)">Adjusted Score</div>
        <div style="margin-top:4px;font-size:12px;color:${result.overall_score >= currentResults.overall_score ? "var(--accent-green)" : "var(--accent-red)"}">
          ${result.overall_score >= currentResults.overall_score ? "▲" : "▼"} ${Math.abs(result.overall_score - currentResults.overall_score)} pts from base (${currentResults.overall_score})
        </div>
        <div style="margin-top:4px;font-size:12px;color:${result.recommendation.color}">${result.recommendation.level}</div>
      `;
    } catch (e) {
      /* ignore */
    }
  }, 200);
}

async function applyWhatIfPreset(name) {
  try {
    const res = await fetch("/api/what-if/presets");
    const presets = await res.json();
    const preset = presets.find((p) => p.name === name);
    if (!preset || !currentResults) return;

    Object.entries(preset.adjustments).forEach(([key, val]) => {
      const el = document.getElementById(`wi-${key}`);
      if (el) el.value = val;
    });

    const tabBtn = document.querySelector("#results-tabs .tab:nth-child(3)");
    if (tabBtn) switchResultsTab("whatif", tabBtn);
    updateWhatIfPreview();
  } catch (e) {
    /* ignore */
  }
}

/* === REMEDIATION TAB === */

async function renderRemediationTab() {
  if (!currentResults) return;
  const container = document.getElementById("tab-remediation");
  const dims = currentResults.dimension_scores;

  let remediation;
  try {
    const res = await fetch("/api/remediation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dimension_scores: dims }),
    });
    remediation = await res.json();
  } catch (e) {
    container.innerHTML =
      '<p style="color:var(--text-muted)">Remediation data unavailable.</p>';
    return;
  }

  const dimLabels = {
    data_quality: "Data Quality",
    process_stability: "Process Stability",
    exception_rate: "Exception Rate",
    decision_complexity: "Decision Complexity",
    integration_readiness: "Tool Integration",
    governance_risk: "Governance Risk",
    roi_potential: "ROI Potential",
  };

  const severityColors = {
    Critical: "var(--accent-red)",
    High: "var(--accent-orange)",
    Medium: "var(--accent-yellow)",
    Low: "var(--accent-green)",
  };

  container.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
      <h3 style="margin:0">Remediation Playbooks</h3>
      ${
        remediation.timeline
          ? `
        <div style="font-size:13px;color:var(--text-muted)">
          Estimated: <strong>${remediation.timeline.estimated_total_weeks} weeks</strong> (${remediation.timeline.estimated_months} months) ·
          Teams: ${remediation.timeline.teams_involved.join(", ")}
        </div>
      `
          : ""
      }
    </div>
    ${Object.entries(dimLabels)
      .map(([key, label]) => {
        const plan = remediation.playbook?.[key];
        if (!plan) return "";
        return `<div style="background:var(--bg-input);border-radius:10px;padding:16px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <strong>${label}</strong>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:12px;color:var(--text-muted)">Score: ${plan.current_score}</span>
            <span style="font-size:11px;padding:2px 8px;border-radius:4px;background:${severityColors[plan.severity] || "var(--text-muted)"}20;color:${severityColors[plan.severity] || "var(--text-muted)"}">${plan.severity}</span>
          </div>
        </div>
        <div style="display:grid;gap:8px">
          ${plan.phases
            .map(
              (p) => `
            <div style="background:var(--bg-card);border-radius:8px;padding:12px;border-left:3px solid var(--accent-blue)">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <strong style="font-size:13px">${p.name}</strong>
                <span style="font-size:11px;color:var(--text-muted)">${p.effort} · ${p.team}</span>
              </div>
              <ul style="margin:0;padding-left:16px;font-size:12px;color:var(--text-secondary)">
                ${p.actions.map((a) => `<li style="margin:2px 0">${a}</li>`).join("")}
              </ul>
            </div>
          `,
            )
            .join("")}
        </div>
      </div>`;
      })
      .join("")}
  `;
}

/* === REGULATORY TAB === */

async function renderRegulatoryTab() {
  if (!currentResults) return;
  const container = document.getElementById("tab-regulatory");
  const r = currentResults;
  const industry = document.getElementById("wf-industry").value || "Unknown";
  const dims = r.dimension_scores;

  let regulatory;
  try {
    const res = await fetch("/api/regulations/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ industry, dimension_scores: dims }),
    });
    regulatory = await res.json();
  } catch (e) {
    container.innerHTML =
      '<p style="color:var(--text-muted)">Regulatory data unavailable.</p>';
    return;
  }

  const details = regulatory.regulation_details || [];

  container.innerHTML = `
    <h3 style="margin-bottom:16px">Applicable Regulations for ${industry}</h3>
    ${
      regulatory.applicable_regulations?.length > 0
        ? `
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
        ${regulatory.applicable_regulations
          .map(
            (reg) =>
              `<span class="tag tag-info" style="font-size:13px;padding:4px 12px">${reg}</span>`,
          )
          .join("")}
      </div>
    `
        : '<p style="color:var(--text-muted);margin-bottom:16px">No specific regulatory frameworks matched.</p>'
    }
    <div class="dashboard-grid" style="margin-bottom:16px">
      <div class="score-card"><div style="font-size:18px;font-weight:600;color:var(--accent-orange)">${regulatory.aggregate_governance_penalty || 0}</div><div class="dim-label">Governance Penalty (applied)</div></div>
      <div class="score-card"><div style="font-size:18px;font-weight:600;color:var(--accent-blue)">${regulatory.effective_data_quality_cap || 100}</div><div class="dim-label">Effective Data Quality Cap</div></div>
    </div>
    ${regulatory.approval_required ? `<div class="risk-item" style="border-left-color:var(--accent-yellow)"><p style="font-size:13px;color:var(--accent-yellow)">⚠️ Human approval is required for automated decisions under applicable regulations.</p></div>` : ""}
    ${regulatory.human_override_mandatory ? `<div class="risk-item" style="border-left-color:var(--accent-orange)"><p style="font-size:13px;color:var(--accent-orange)">🔒 Human override capability is mandatory for automated systems under applicable regulations.</p></div>` : ""}
    <h3 style="margin:24px 0 12px">Regulation Details</h3>
    ${details
      .map(
        (d) => `
      <div style="background:var(--bg-input);border-radius:10px;padding:16px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px">
          <div>
            <strong style="font-size:14px">${d.framework}</strong>
            <span style="font-size:11px;color:var(--text-muted);margin-left:8px">${d.key} · ${d.jurisdiction}</span>
          </div>
          <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:rgba(249,115,22,0.15);color:var(--accent-orange)">Penalty: ${d.governance_penalty}</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
          <div style="font-size:12px;color:var(--text-muted)">Audit: ${d.audit_frequency}</div>
          <div style="font-size:12px;color:var(--text-muted)">Quality cap: ${d.data_quality_cap}</div>
          <div style="font-size:12px;color:var(--text-muted)">Approval needed: ${d.approval_required ? "Yes" : "No"}</div>
          <div style="font-size:12px;color:var(--text-muted)">Human override: ${d.human_override_mandatory ? "Mandatory" : "Not required"}</div>
        </div>
        <div style="padding:8px;background:var(--bg-card);border-radius:6px;font-size:12px;color:var(--text-secondary)">
          ⚠️ ${d.risk_statement}
        </div>
      </div>
    `,
      )
      .join("")}
  `;
}

/* === AI / LLM FUNCTIONS === */

async function checkLlmStatus() {
  const dot = document.getElementById("llm-status-dot");
  const text = document.getElementById("llm-status-text");
  const banner = document.getElementById("llm-status-banner");
  const guide = document.getElementById("llm-setup-guide");
  const btn = document.getElementById("btn-ai-infer");

  if (!dot || !text) return;

  try {
    const res = await fetch("/api/llm/status");
    const status = await res.json();

    if (status.available && status.model_loaded) {
      llmAvailable = true;
      dot.style.background = "var(--accent-green)";
      text.textContent = `${status.model} (connected)`;
      text.style.color = "var(--accent-green)";
      if (btn) btn.disabled = false;
      if (banner) {
        banner.style.display = "none";
        banner.innerHTML = "";
      }
      if (guide) guide.style.display = "none";
    } else if (status.configured && !status.model_loaded) {
      dot.style.background = "var(--accent-yellow)";
      text.textContent = "Model not loaded — load it in LM Studio";
      text.style.color = "var(--accent-yellow)";
      if (btn) btn.disabled = true;
      if (banner) {
        banner.style.display = "block";
        banner.className = "alert";
        banner.style.cssText =
          "background:rgba(234,179,8,0.1);border:1px solid rgba(234,179,8,0.3);color:var(--accent-yellow);border-radius:8px;padding:12px;margin-bottom:12px;font-size:13px";
        banner.innerHTML = `<strong>⚠️ Model not loaded.</strong> Start <code>${status.model}</code> in LM Studio, or set a different model in <code>.env</code>. Available: ${(status.available_models || ["none"]).join(", ")}`;
      }
      if (guide) guide.style.display = "none";
    } else if (status.configured && !status.available) {
      dot.style.background = "var(--accent-orange)";
      text.textContent = "LM Studio unreachable";
      text.style.color = "var(--accent-orange)";
      if (btn) btn.disabled = true;
      if (banner) {
        banner.style.display = "block";
        banner.className = "alert";
        banner.style.cssText =
          "background:rgba(249,115,22,0.1);border:1px solid rgba(249,115,22,0.3);color:var(--accent-orange);border-radius:8px;padding:12px;margin-bottom:12px;font-size:13px";
        banner.innerHTML = `<strong>🔌 LLM endpoint unreachable.</strong> Check that LM Studio is running at <code>${status.endpoint}</code>. The deterministic engine works without AI.`;
      }
      if (guide) guide.style.display = "none";
    } else {
      llmAvailable = false;
      dot.style.background = "var(--text-muted)";
      text.textContent = "Not configured — optional";
      text.style.color = "var(--text-muted)";
      if (btn) btn.disabled = true;
      if (banner) {
        banner.style.display = "none";
        banner.innerHTML = "";
      }
      if (guide) guide.style.display = "block";
      document.getElementById("use-llm").checked = false;
    }
  } catch (e) {
    dot.style.background = "var(--accent-red)";
    text.textContent = "Status check failed";
    if (guide) guide.style.display = "block";
  }
}

/* === EXAMPLE WORKFLOWS — quick start === */

const EXAMPLES = [
  {
    name: "Invoice Processing",
    industry: "Manufacturing",
    desc: "We process incoming invoices from 50+ vendors across 3 countries. Each vendor submits in a different format — PDF via email, EDI, supplier portal uploads, and some still fax. Our AP team of 5 manually enters data into SAP. About 30% have mismatches (PO number typos, amount discrepancies, missing tax IDs) requiring back-and-forth with vendors. Approvals follow a multi-tier workflow: manager up to $5k, director up to $50k, CFO above. We handle ~1,200 invoices per month. Audit requires full traceability for intercompany transactions. Payment terms are Net30 but we average Net45 due to processing delays.",
  },
  {
    name: "Support Ticket Routing",
    industry: "SaaS",
    desc: "Our B2B SaaS platform receives ~3,000 support tickets per month across email, chat, and in-app. Tier 1 handles password resets, account lookups, and billing inquiries (~60% of volume). Tier 2 handles API integration issues, data export problems, and configuration help (~30%). Tier 3 escalates to engineering for bugs (~10%). We use Zendesk but routing is manual — an agent reads and assigns each ticket. Peak hours (Mon 9-12) see 3x volume and 4+ hour wait times. SLAs require 4-hour response for standard, 1-hour for premium customers. CSAT is 82%. We have playbooks for common issues but agents don't always follow them.",
  },
  {
    name: "Claims Adjudication",
    industry: "Insurance",
    desc: "We process health insurance claims for 200k+ members. Each claim goes through eligibility verification, service coding check (CPT/ICD-10), benefit calculation, and payment determination. Our team of 12 adjusters handles ~500 claims/day. 40% of claims auto-adjudicate; the rest need manual review due to coding mismatches, non-covered services, coordination of benefits, or out-of-network pricing. Fraud detection flags ~5% for investigation. We're regulated by HIPAA, state insurance departments, and NCQA. Audit trails are mandatory. Appeal rate is 8%. Average processing time is 14 days — we need to get to 7. System runs on a 20-year-old mainframe with a modern UI layer.",
  },
  {
    name: "Employee Onboarding",
    industry: "Human Resources",
    desc: "We onboard 50-80 new hires per month across 4 countries. The process spans HR (offer letters, background checks, I-9 verification), IT (laptop provisioning, account creation, software licensing), Facilities (badge access, desk assignment), and Payroll (bank details, tax forms, benefits enrollment). Each department uses a different system — Workday, ServiceNow, Jira, and a custom payroll app. There's no central tracking; coordinators use spreadsheets and email reminders. 25% of new hires experience delays because a step was missed. Compliance requires documented evidence of I-9 and background check completion within 3 days. First-day frustration is high when laptops or access aren't ready.",
  },
  {
    name: "Mortgage Processing",
    industry: "Banking",
    desc: "We originate ~200 mortgages per month. Process starts with pre-qualification, then full application, document collection (pay stubs, tax returns, bank statements, W-2s), credit pull, appraisal order, underwriting, conditional approval, and closing. Loan officers, processors, underwriters, and closers work across Encompass, BlitzDocs, and email. Documents arrive via upload, fax, and mail — many are handwritten or scanned poorly. Underwriters manually extract income data and calculate DTI ratios. Regulatory compliance under TRID, RESPA, and ECOA requires strict timing disclosures and audit trails. Average cycle time is 38 days. 15% of applications fall out due to missing documents not requested in time. Error rate in data entry is ~8%.",
  },
  {
    name: "Order Fulfillment",
    industry: "Retail",
    desc: "We run an e-commerce operation doing ~15,000 orders/month across Shopify, Amazon FBA, and a wholesale B2B channel. Fulfillment involves: order import, inventory allocation, pick list generation, warehouse picking, packing, label printing, and carrier handoff. We use ShipStation but inventory sync between Shopify and our warehouse WMS is manual via CSV export/import. Peak season (Nov-Dec) sees 4x volume. 12% of orders have picking errors (wrong variant, wrong quantity). Returns processing is entirely manual — 8% return rate, each takes 15 minutes to inspect, restock, and process refund. Carrier rate shopping is done manually. Our warehouse team of 8 works 6 days a week during peak. Real-time inventory visibility across channels doesn't exist — we oversell about 3% of the time.",
  },
];

function loadExample(index) {
  const ex = EXAMPLES[index];
  if (!ex) return;

  document.getElementById("wf-name").value = ex.name;
  document.getElementById("wf-industry").value = ex.industry;
  document.getElementById("wf-desc").value = ex.desc;

  document
    .getElementById("wf-desc")
    .scrollIntoView({ behavior: "smooth", block: "center" });
  document.getElementById("wf-desc").focus();

  document.querySelectorAll("#example-cards .example-card").forEach((el, i) => {
    el.style.borderColor = i === index ? "var(--accent-blue)" : "var(--border)";
    el.style.background = i === index ? "rgba(59,130,246,0.12)" : "";
  });

  if (llmAvailable) {
    aiInferWorkflow();
  }
}

async function aiInferWorkflow() {
  const name = document.getElementById("wf-name").value;
  const industry = document.getElementById("wf-industry").value;
  const desc = document.getElementById("wf-desc").value;
  const resultsDiv = document.getElementById("llm-infer-results");
  const btn = document.getElementById("btn-ai-infer");

  if (!desc && !name) {
    resultsDiv.style.display = "block";
    resultsDiv.innerHTML = `<div class="alert alert-danger">Describe your workflow first — or enter at least a workflow name.</div>`;
    return;
  }

  const fullDesc =
    [name, industry, desc].filter(Boolean).join(" — ") || "Unknown workflow";
  btn.disabled = true;
  btn.innerHTML = "⏳ Analyzing...";
  resultsDiv.style.display = "block";
  resultsDiv.innerHTML =
    '<div style="color:var(--text-muted);font-size:13px">🧠 Querying LLM...</div>';

  try {
    const res = await fetch("/api/llm/infer-workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: fullDesc, industry }),
    });

    if (!res.ok) {
      const err = await res.json();
      resultsDiv.innerHTML = `<div class="alert alert-danger">${err.error || "LLM inference failed"}</div>`;
      return;
    }

    const data = await res.json();
    const scores = data.dimension_scores || {};

    const dimRes = await fetch("/api/dimensions");
    const dims = await dimRes.json();
    window.__dimensionsCache = dims;

    Object.entries(dims).forEach(([key, dim]) => {
      if (scores[key] !== undefined) {
        const val = scores[key];
        const aggInput = document.getElementById(`input-agg-${key}`);
        const aggDisplay = document.getElementById(`display-agg-${key}`);
        if (aggInput) aggInput.value = val;
        if (aggDisplay) aggDisplay.textContent = val;

        dim.questions.forEach((q) => {
          const subInput = document.getElementById(`input-${q.id}`);
          const subDisplay = document.getElementById(`display-${q.id}`);
          if (subInput) subInput.value = val;
          if (subDisplay) subDisplay.textContent = val;
        });

        updateDimTier("", key, val);
      }
    });

    updateLivePreview();

    let html = `
      <div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.2);border-radius:8px;padding:12px;margin-bottom:8px">
        <strong style="color:var(--accent-green);font-size:13px">✅ Scores pre-filled from LLM analysis</strong>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
        ${Object.entries(scores)
          .map(([key, val]) => {
            const label = dims[key]?.label || key;
            const color =
              val >= 70
                ? "var(--accent-green)"
                : val >= 50
                  ? "var(--accent-yellow)"
                  : "var(--accent-orange)";
            return `<div style="background:var(--bg-input);border-radius:6px;padding:8px;text-align:center">
            <div style="font-size:18px;font-weight:700;color:${color}">${val}</div>
            <div style="font-size:11px;color:var(--text-muted)">${label}</div>
          </div>`;
          })
          .join("")}
      </div>
    `;

    if (data.reasoning) {
      html += `<div style="margin-top:8px;padding:8px;background:var(--bg-card);border-radius:6px;font-size:12px;color:var(--text-secondary)">${data.reasoning}</div>`;
    }
    if (
      data.suggested_sub_processes &&
      data.suggested_sub_processes.length > 0
    ) {
      html += `<div style="margin-top:8px;font-size:12px;color:var(--text-muted)">Suggested sub-processes: ${data.suggested_sub_processes.join(", ")}</div>`;
    }

    resultsDiv.innerHTML = html;
  } catch (e) {
    resultsDiv.innerHTML = `<div class="alert alert-danger">Failed to reach LLM. Is LM Studio running?</div>`;
  }

  btn.disabled = false;
  btn.innerHTML = "🪄 Auto-fill Scores from Description";
}

/* === AI SUMMARY TAB === */

function renderAiTab() {
  const container = document.getElementById("tab-ai");
  if (!currentResults) {
    container.innerHTML =
      "<p style='color:var(--text-muted)'>No results to summarize.</p>";
    return;
  }

  const r = currentResults;

  if (!r.llm_summary && !r.llm_risks) {
    container.innerHTML = `
      <div style="text-align:center;padding:32px">
        <div style="font-size:48px;margin-bottom:16px">🧠</div>
        <h3 style="margin-bottom:8px">AI Enrichment Not Available</h3>
        <p style="color:var(--text-secondary);max-width:500px;margin:0 auto">
          Results were not enriched with AI. This analysis uses the deterministic engine only.
          Configure LLM inference (LM Studio or compatible) and re-run with "Enrich results with AI" enabled
          to get contextual risk analysis, executive summaries, and deeper insights.
        </p>
      </div>
    `;
    return;
  }

  let html = "";

  if (r.llm_summary) {
    const s = r.llm_summary;
    html += `
      <div style="margin-bottom:20px">
        <h3 style="margin-bottom:8px">Executive Summary</h3>
        <div style="background:var(--bg-input);border-radius:10px;padding:16px;line-height:1.7">
          ${s.executive_summary ? `<p style="color:var(--text-secondary);font-size:14px">${s.executive_summary}</p>` : ""}
        </div>
        ${
          s.key_findings && s.key_findings.length > 0
            ? `
          <div style="margin-top:12px">
            <strong style="font-size:13px">Key Findings</strong>
            <ul style="margin:8px 0;padding-left:20px;font-size:13px;color:var(--text-secondary)">
              ${s.key_findings.map((f) => `<li style="margin:4px 0">${f}</li>`).join("")}
            </ul>
          </div>
        `
            : ""
        }
        ${
          s.recommendation
            ? `
          <div style="margin-top:12px;padding:12px;background:var(--bg-card);border-radius:8px;font-size:14px;font-weight:600">
            ${s.recommendation}
          </div>
        `
            : ""
        }
        ${
          s.risk_statement
            ? `
          <div style="margin-top:8px;padding:10px;background:rgba(239,68,68,0.05);border-radius:6px;font-size:13px;color:var(--accent-red)">
            ⚠️ ${s.risk_statement}
          </div>
        `
            : ""
        }
      </div>
    `;
  }

  if (r.llm_risks && r.llm_risks.length > 0) {
    html += `
      <h3 style="margin-bottom:12px">AI-Identified Risks</h3>
      <div class="failure-grid">
        ${r.llm_risks
          .map((risk) => {
            const sevClass =
              (risk.severity || "").toLowerCase() === "critical"
                ? "severity-critical"
                : (risk.severity || "").toLowerCase() === "high"
                  ? "severity-high"
                  : (risk.severity || "").toLowerCase() === "medium"
                    ? "severity-medium"
                    : "severity-low";
            return `<div class="failure-card">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px">
              <strong style="font-size:14px">${risk.mode}</strong>
              <span class="failure-severity ${sevClass}">${risk.severity}</span>
            </div>
            <p style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${risk.description}</p>
            <div style="display:flex;gap:12px;font-size:12px;color:var(--text-muted);margin-bottom:6px">
              <span>Likelihood: ${risk.likelihood}</span>
              <span>Detectability: ${risk.detectability}</span>
            </div>
            <div style="padding:8px;background:var(--bg-card);border-radius:6px;font-size:12px;color:var(--accent-blue)">
              💡 ${risk.mitigation}
            </div>
          </div>`;
          })
          .join("")}
      </div>
    `;
  }

  container.innerHTML = html;
}

/* === BENCHMARK === */

async function loadBenchmarkStats() {
  try {
    const res = await fetch("/api/benchmark/stats");
    const stats = await res.json();
    const catColors = {
      "AGENT AUTOMATION READY": "#22c55e",
      "AI ASSISTED AUTOMATION": "#3b82f6",
      "HUMAN-IN-THE-LOOP AI": "#eab308",
      "IMPROVE PROCESS FIRST": "#f97316",
      "DO NOT AUTOMATE": "#ef4444",
    };
    const container = document.getElementById("benchmark-stats");
    container.innerHTML = `
      <div class="stats-row">
        <div class="stat-card"><div class="stat-value" style="color:var(--accent-blue)">${stats.total}</div><div class="stat-label">Workflows</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--accent-green)">${stats.industries}</div><div class="stat-label">Industries</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--accent-yellow)">${stats.overall_average}</div><div class="stat-label">Avg Score</div></div>
        ${Object.entries(stats.by_category || {})
          .map(
            ([cat, count]) =>
              `<div class="stat-card"><div class="stat-value" style="font-size:16px;color:${catColors[cat] || "#9aa0b0"}">${count}</div><div class="stat-label">${cat}</div></div>`,
          )
          .join("")}
      </div>
    `;
  } catch (e) {
    /* ignore */
  }
}

async function loadBenchmark() {
  const container = document.getElementById("benchmark-results");
  container.innerHTML =
    '<div class="loading"><div class="spinner"></div><p>Loading benchmark...</p></div>';
  const industry = document.getElementById("bf-industry").value;
  const category = document.getElementById("bf-category").value;
  const query = document.getElementById("bf-search").value;

  try {
    let url = "/api/benchmark?limit=100";
    if (industry) url += `&industry=${encodeURIComponent(industry)}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (query) url += `&q=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    const wfs = await res.json();
    const catColors = {
      "AGENT AUTOMATION READY": "#22c55e",
      "AI ASSISTED AUTOMATION": "#3b82f6",
      "HUMAN-IN-THE-LOOP AI": "#eab308",
      "IMPROVE PROCESS FIRST": "#f97316",
      "DO NOT AUTOMATE": "#ef4444",
    };

    container.innerHTML = `
      <p style="color:var(--text-secondary);margin-bottom:12px">Showing ${wfs.length} workflows</p>
      <div style="overflow-x:auto">
        <table class="bench-table">
          <thead><tr>
            <th>Score</th><th>Industry</th><th>Workflow</th><th>Category</th><th>Failures</th><th>Volume</th><th>Tooling</th>
          </tr></thead>
          <tbody>
            ${wfs
              .map(
                (w) => `
              <tr onclick="showWorkflowDetail(${w.id})" style="cursor:pointer">
                <td class="score-cell" style="color:${w.scores.overall_score >= 70 ? "#22c55e" : w.scores.overall_score >= 50 ? "#eab308" : w.scores.overall_score >= 30 ? "#f97316" : "#ef4444"}">${w.scores.overall_score}</td>
                <td>${w.industry}</td>
                <td><strong>${w.workflow_name}</strong></td>
                <td><span class="tag" style="background:${catColors[w.category] || "#6b7280"}20;color:${catColors[w.category] || "#6b7280"}">${w.category}</span></td>
                <td>${w.failures
                  .slice(0, 2)
                  .map((f) => `<span class="tag tag-danger">${f}</span>`)
                  .join(
                    "",
                  )}${w.failures.length > 2 ? `<span class="tag" style="background:var(--bg-input);color:var(--text-muted)">+${w.failures.length - 2}</span>` : ""}</td>
                <td style="font-size:12px;color:var(--text-muted)">${w.metadata.annual_volume}</td>
                <td style="font-size:12px;color:var(--text-muted)">${w.metadata.current_tooling}</td>
              </tr>
            `,
              )
              .join("")}
          </tbody>
        </table>
      </div>
    `;
  } catch (e) {
    container.innerHTML =
      '<div class="alert alert-danger">Failed to load benchmark data.</div>';
  }
}

function showWorkflowDetail(id) {
  fetch("/api/benchmark?limit=600")
    .then((r) => r.json())
    .then((wfs) => {
      const w = wfs.find((x) => x.id === id);
      if (!w) return;
      const s = w.scores;
      const catColors = {
        "AGENT AUTOMATION READY": "#22c55e",
        "AI ASSISTED AUTOMATION": "#3b82f6",
        "HUMAN-IN-THE-LOOP AI": "#eab308",
        "IMPROVE PROCESS FIRST": "#f97316",
        "DO NOT AUTOMATE": "#ef4444",
      };
      const dimLabels = {
        data_quality: "Data Quality",
        process_stability: "Process Stability",
        exception_rate: "Exception Rate",
        decision_complexity: "Decision Complexity",
        integration_readiness: "Tool Integration",
        governance_risk: "Governance Risk",
        roi_potential: "ROI Potential",
      };
      const container = document.getElementById("benchmark-results");
      container.innerHTML = `
        <div class="card"><div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:12px">
          <div><h2 style="margin-bottom:4px">${w.workflow_name}</h2><p style="color:var(--text-secondary)">${w.industry} — ${w.description}</p></div>
          <div style="text-align:right">
            <div style="font-size:42px;font-weight:700;color:${s.overall_score >= 70 ? "#22c55e" : s.overall_score >= 50 ? "#eab308" : s.overall_score >= 30 ? "#f97316" : "#ef4444"}">${s.overall_score}</div>
            <div style="font-size:12px;color:var(--text-muted)">Score</div>
            <span class="tag" style="background:${catColors[w.category] || "#6b7280"}20;color:${catColors[w.category] || "#6b7280"};padding:4px 12px">${w.category}</span>
          </div>
        </div></div>
        <div class="dashboard-grid">
          <div class="card"><div class="card-title">Scores</div><div class="scores-grid">${Object.entries(
            dimLabels,
          )
            .map(([key, label]) => {
              const val = s[key] || 0;
              const color =
                val >= 70
                  ? "#22c55e"
                  : val >= 50
                    ? "#eab308"
                    : val >= 30
                      ? "#f97316"
                      : "#ef4444";
              return `<div class="score-card"><div class="value" style="color:${color};font-size:24px">${val}</div><div class="dim-label">${label}</div></div>`;
            })
            .join("")}</div></div>
          <div class="card"><div class="card-title">Metadata</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
              ${Object.entries(w.metadata)
                .map(
                  ([k, v]) =>
                    `<div style="padding:8px;background:var(--bg-input);border-radius:6px"><span style="color:var(--text-muted);font-size:11px">${k.replace(/_/g, " ")}</span><p style="font-size:14px">${v}</p></div>`,
                )
                .join("")}
            </div>
          </div>
        </div>
        <div class="card"><div class="card-title">Injected Failures</div><div style="display:flex;flex-wrap:wrap;gap:8px">
          ${w.failures.map((f) => `<span class="tag tag-danger">${f}</span>`).join("")}
          ${w.failures.length === 0 ? '<span style="color:var(--text-muted);font-size:13px">Clean workflow</span>' : ""}
        </div></div>
        <div class="card" style="text-align:center"><button class="btn btn-secondary" onclick="loadBenchmark()">← Back</button></div>
      `;
    });
}

/* === NAVIGATION === */

function showSection(name) {
  document
    .querySelectorAll(".section")
    .forEach((s) => s.classList.remove("active"));
  document
    .querySelectorAll(".nav-links a")
    .forEach((a) => a.classList.remove("active"));
  document.getElementById(`section-${name}`).classList.add("active");
  const link =
    document.querySelector(`.nav-links a[onclick*="'${name}'"]`) ||
    document.querySelector(`.nav-links a[onclick*="${name}"]`);
  if (link) link.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

(async function initFilters() {
  try {
    const [industries, categories] = await Promise.all([
      fetch("/api/benchmark/industries").then((r) => r.json()),
      fetch("/api/benchmark/categories").then((r) => r.json()),
    ]);
    const indSelect = document.getElementById("bf-industry");
    industries.forEach((i) => {
      const o = document.createElement("option");
      o.value = i;
      o.textContent = i;
      indSelect.appendChild(o);
    });
    const catSelect = document.getElementById("bf-category");
    categories.forEach((c) => {
      const o = document.createElement("option");
      o.value = c;
      o.textContent = c;
      catSelect.appendChild(o);
    });
  } catch (e) {
    /* ignore */
  }
})();
