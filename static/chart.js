/* ══════════════════════════════════════════════════════
   EMI Stress Tester — Frontend Logic
   ══════════════════════════════════════════════════════ */

"use strict";

// ── Chart instances (kept so we can destroy & recreate) ──
let cashflowChartInstance = null;
let savingsChartInstance  = null;

// ── Helpers ───────────────────────────────────────────────
const fmt = (n) =>
  "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 });

const fmtRatio = (n) => Number(n).toFixed(1) + "%";

function el(id) { return document.getElementById(id); }

// ── Form submit ───────────────────────────────────────────
el("stressForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const form   = e.target;
  const errBox = el("formError");
  errBox.hidden = true;

  // Collect values
  const income         = parseFloat(el("income").value)         || 0;
  const savings        = parseFloat(el("savings").value)        || 0;
  const home_emi       = parseFloat(el("home_emi").value)       || 0;
  const car_emi        = parseFloat(el("car_emi").value)        || 0;
  const personal_emi   = parseFloat(el("personal_emi").value)   || 0;
  const other_emi      = parseFloat(el("other_emi").value)      || 0;
  const living_expense = parseFloat(el("living_expense").value) || 0;
  const loan_amount    = parseFloat(el("loan_amount").value)    || 0;
  const loan_rate      = parseFloat(el("loan_rate").value)      || 0;
  const loan_tenure    = parseFloat(el("loan_tenure").value)    || 0;

  // Basic validation
  if (income <= 0) {
    errBox.textContent = "Please enter a valid monthly income.";
    errBox.hidden = false;
    return;
  }

  // Show loading
  el("loadingOverlay").hidden = false;
  el("submitBtn").classList.add("loading");

  try {
    const resp = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        income, savings, home_emi, car_emi, personal_emi, other_emi,
        living_expense, loan_amount, loan_rate, loan_tenure,
      }),
    });

    if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
    const d = await resp.json();

    renderResults(d, savings);

  } catch (err) {
    errBox.textContent = "Analysis failed: " + err.message;
    errBox.hidden = false;
  } finally {
    el("loadingOverlay").hidden = true;
    el("submitBtn").classList.remove("loading");
  }
});

// ── Render all results ────────────────────────────────────
function renderResults(d, currentSavings) {
  const panel = el("resultsPanel");
  panel.hidden = false;

  // Scroll results into view on mobile
  panel.scrollIntoView({ behavior: "smooth", block: "start" });

  renderVerdict(d);
  renderMetrics(d);
  renderRecommendation(d);
  renderCashflowChart(d);
  renderSavingsChart(d, currentSavings);
}

// ── Verdict card ──────────────────────────────────────────
function renderVerdict(d) {
  const card     = el("verdictCard");
  const badge    = el("verdictBadge");
  const text     = el("verdictText");
  const prob     = el("verdictProb");
  const survival = el("verdictSurvival");
  const fill     = el("gaugeFill");
  const label    = el("gaugeLabel");

  // Clear classes
  card.className = "verdict-card";
  const iconMap    = { "Safe": "✓", "At Risk": "⚠", "High Risk": "✕" };
  const classMap   = { "Safe": "safe", "At Risk": "at-risk", "High Risk": "high-risk" };

  card.classList.add(classMap[d.verdict] || "");
  badge.querySelector("span").textContent = iconMap[d.verdict] || "?";
  text.textContent = d.verdict;
  prob.textContent = `${d.default_probability}% default risk`;
  survival.textContent = `You can survive ${d.survival_months} month${d.survival_months !== 1 ? "s" : ""} without income`;

  // Gauge — arc spans 157px dasharray; fill proportionally to default_probability/100
  const pct = Math.min(d.default_probability / 100, 1);
  fill.style.strokeDashoffset = 157 - pct * 157;
  label.textContent = d.default_probability + "%";
}

// ── Metric cards ──────────────────────────────────────────
function renderMetrics(d) {
  el("mBurn").textContent     = fmt(d.total_burn);
  el("mBurnRatio").textContent = fmtRatio(d.burn_to_income_ratio);
  el("mNewEmi").textContent   = fmt(d.new_emi);
  el("mTotalEmi").textContent = fmt(d.total_emis_after);
}

// ── Recommendation box ────────────────────────────────────
function renderRecommendation(d) {
  const rows = el("recRows");
  rows.innerHTML = "";

  const addRow = (key, val, cls = "") =>
    rows.insertAdjacentHTML("beforeend",
      `<div class="rec-row">
         <span class="rec-key">${key}</span>
         <span class="rec-val ${cls}">${val}</span>
       </div>`);

  addRow("Your current living expense", fmt(d.living_expense));
  addRow("Recommended maximum",
    d.recommended_living > 0 ? fmt(d.recommended_living) : "—",
    d.recommended_living <= 0 ? "bad" : "ok"
  );

  if (d.recommended_living < 0) {
    rows.insertAdjacentHTML("beforeend",
      `<div class="rec-alert bad">
         ⚠️ Your EMIs alone exceed the safe burn rate. Consider restructuring existing loans before taking a new one.
       </div>`);
  } else if (d.reduction_needed <= 0) {
    rows.insertAdjacentHTML("beforeend",
      `<div class="rec-alert ok">
         ✅ Your living expenses are within safe limits.
       </div>`);
  } else {
    addRow("You need to reduce by", fmt(d.reduction_needed), "warn");
    rows.insertAdjacentHTML("beforeend",
      `<div class="rec-alert warn">
         ⚡ Reducing monthly expenses by ${fmt(d.reduction_needed)} would give you a 3-month safety cushion.
       </div>`);
  }
}

// ── Chart 1: Horizontal bar — cash flow breakdown ────────
function renderCashflowChart(d) {
  const ctx = el("cashflowChart").getContext("2d");
  if (cashflowChartInstance) cashflowChartInstance.destroy();

  const remaining = Math.max(d.income - d.total_burn, 0);

  cashflowChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Income", "Total EMIs", "Living Expenses", "Remaining"],
      datasets: [{
        data: [d.income, d.total_emis_after, d.living_expense, remaining],
        backgroundColor: [
          "rgba(36,81,160,0.85)",
          "rgba(214,64,69,0.85)",
          "rgba(232,160,32,0.85)",
          "rgba(29,158,117,0.85)",
        ],
        borderColor: [
          "rgba(36,81,160,1)",
          "rgba(214,64,69,1)",
          "rgba(232,160,32,1)",
          "rgba(29,158,117,1)",
        ],
        borderWidth: 1.5,
        borderRadius: 5,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => " " + fmt(ctx.raw),
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(0,0,0,0.06)" },
          ticks: {
            callback: (v) => "₹" + (v >= 1000 ? (v / 1000).toFixed(0) + "k" : v),
            font: { size: 10 },
          },
        },
        y: { grid: { display: false }, ticks: { font: { size: 11 } } },
      },
    },
  });
}

// ── Chart 2: Line — savings drain over 3 stress months ───
function renderSavingsChart(d, initialSavings) {
  const ctx = el("savingsChart").getContext("2d");
  if (savingsChartInstance) savingsChartInstance.destroy();

  const dataPoints = [
    initialSavings,
    d.savings_after_1m,
    d.savings_after_2m,
    d.savings_after_3m,
  ];

  savingsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Month 0", "Month 1", "Month 2", "Month 3"],
      datasets: [
        {
          label: "Savings (₹)",
          data: dataPoints,
          borderColor: "rgba(36,81,160,1)",
          backgroundColor: "rgba(36,81,160,0.12)",
          pointBackgroundColor: dataPoints.map((v) =>
            v < 0 ? "rgba(214,64,69,1)" : "rgba(36,81,160,1)"
          ),
          pointRadius: 5,
          pointHoverRadius: 7,
          tension: 0.35,
          fill: true,
          borderWidth: 2.5,
        },
        {
          // Zero line annotation (red dashed)
          label: "Zero savings",
          data: [0, 0, 0, 0],
          borderColor: "rgba(214,64,69,0.7)",
          borderDash: [6, 4],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { boxWidth: 14, font: { size: 11 } },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => " " + fmt(ctx.raw),
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: {
          grid: { color: "rgba(0,0,0,0.06)" },
          ticks: {
            callback: (v) => "₹" + (Math.abs(v) >= 1000
              ? (v / 1000).toFixed(0) + "k" : v),
            font: { size: 10 },
          },
        },
      },
    },
  });
}
