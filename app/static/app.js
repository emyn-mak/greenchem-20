const sampleFormula = `20 mL H2O
10 mL Acetone
1 mL H2SO4
Temperature: 90C
Time: 4h
Pressure: 1 atm
Stirring: 300 rpm
pH: 2
Solvent: Acetone
Catalyst: H2SO4
Catalyst role: acid_catalyst`;

const state = {
  model: null,
  analysis: null,
  simulatedAlternative: null,
  animationFrame: null,
  particles: [],
  lang: "en",
};

const translations = {
  en: {
    "menu.workspace": "Workspace",
    "menu.news": "Chemical news",
    "menu.training": "ML training",
    "brand.title": "Solvent replacement workspace",
    "section.formula": "Formula components",
    "field.waterAmount": "Water amount",
    "field.unit": "Unit",
    "field.solventAmount": "Solvent amount",
    "field.solvent": "Solvent",
    "field.catalystAmount": "Catalyst amount",
    "field.catalyst": "Catalyst",
    "section.conditions": "Reaction conditions",
    "field.temperature": "Temperature",
    "field.time": "Time",
    "field.pressure": "Pressure",
    "field.stirring": "Stirring",
    "field.ph": "pH",
    "field.catalystRole": "Catalyst role",
    "action.analyze": "Analyze",
    "action.sample": "Sample",
    "action.exportPdf": "Export PDF",
    "action.train": "Train compatibility model",
    "action.refreshNews": "Refresh news",
    "action.view3d": "View 3D simulation",
    "metric.alternatives": "Alternatives",
    "metric.validation": "Validation",
    "metric.review": "Human review",
    "hero.ready": "Ready for analysis",
    "hero.readyMessage": "Fill the current process fields to screen greener replacement candidates.",
    "notice.ai": "AI-assisted recommendation only. The final decision must be made by the user or a qualified human expert.",
    "detected.title": "Detected input",
    "assessment.title": "Current assessment",
    "simulation.title": "Replacement simulation",
    "alternatives.title": "Recommended alternatives",
    "news.title": "Chemical news",
    "news.intro": "Recent chemistry and green-chemistry updates for learning and awareness. News does not automatically change recommendations.",
    "training.title": "ML training",
    "training.when": "When to train",
    "training.whenBody": "Train the compatibility model after adding new solvents, catalysts, replacement rules, or reaction examples to the backend knowledge base.",
    "training.whenBody2": "Do not train just because a user typed a new reaction once. First, a qualified person should review the new data and add it to the curated dataset.",
    "training.current": "Current model",
    "training.human": "Human decision",
    "training.humanBody": "ML output is only a signal. The final chemical decision belongs to the user or a qualified human expert.",
    "toast.analysisComplete": "Analysis complete.",
    "toast.pdfExported": "PDF report exported.",
    "toast.needInput": "Enter reaction fields before analysis.",
    "toast.needPdfInput": "Enter reaction fields before exporting a PDF.",
    "toast.needSimulation": "Run analysis first, then select a recommendation to simulate.",
    "loading.news": "Loading news",
    "loading.newsBody": "Fetching recent chemistry updates.",
  },
  fr: {
    "menu.workspace": "Espace de travail",
    "menu.news": "Actualites chimiques",
    "menu.training": "Entrainement ML",
    "brand.title": "Espace de remplacement de solvant",
    "section.formula": "Composants de la formule",
    "field.waterAmount": "Quantite d'eau",
    "field.unit": "Unite",
    "field.solventAmount": "Quantite de solvant",
    "field.solvent": "Solvant",
    "field.catalystAmount": "Quantite de catalyseur",
    "field.catalyst": "Catalyseur",
    "section.conditions": "Conditions de reaction",
    "field.temperature": "Temperature",
    "field.time": "Temps",
    "field.pressure": "Pression",
    "field.stirring": "Agitation",
    "field.ph": "pH",
    "field.catalystRole": "Role du catalyseur",
    "action.analyze": "Analyser",
    "action.sample": "Exemple",
    "action.exportPdf": "Exporter PDF",
    "action.train": "Entrainer le modele",
    "action.refreshNews": "Actualiser",
    "action.view3d": "Voir simulation 3D",
    "metric.alternatives": "Alternatives",
    "metric.validation": "Validation",
    "metric.review": "Revue humaine",
    "hero.ready": "Pret pour l'analyse",
    "hero.readyMessage": "Remplissez les champs du procede actuel pour chercher des solvants plus verts.",
    "notice.ai": "Recommendation assistee par IA uniquement. La decision finale doit etre prise par l'utilisateur ou un expert qualifie.",
    "detected.title": "Entree detectee",
    "assessment.title": "Evaluation actuelle",
    "simulation.title": "Simulation de remplacement",
    "alternatives.title": "Alternatives recommandees",
    "news.title": "Actualites chimiques",
    "news.intro": "Actualites recentes en chimie et chimie verte pour information. Les actualites ne changent pas automatiquement les recommandations.",
    "training.title": "Entrainement ML",
    "training.when": "Quand entrainer",
    "training.whenBody": "Entrainez le modele de compatibilite apres l'ajout de nouveaux solvants, catalyseurs, regles de remplacement ou exemples de reaction dans la base de connaissances.",
    "training.whenBody2": "N'entrainez pas le modele simplement parce qu'un utilisateur a saisi une nouvelle reaction. Un expert doit d'abord verifier les donnees.",
    "training.current": "Modele actuel",
    "training.human": "Decision humaine",
    "training.humanBody": "La sortie ML est seulement un signal. La decision chimique finale appartient a l'utilisateur ou a un expert qualifie.",
    "toast.analysisComplete": "Analyse terminee.",
    "toast.pdfExported": "Rapport PDF exporte.",
    "toast.needInput": "Remplissez les champs avant l'analyse.",
    "toast.needPdfInput": "Remplissez les champs avant l'export PDF.",
    "toast.needSimulation": "Lancez d'abord une analyse, puis choisissez une recommandation a simuler.",
    "loading.news": "Chargement des actualites",
    "loading.newsBody": "Recuperation des actualites chimiques recentes.",
  },
};

const elements = {
  form: document.querySelector("#analysisForm"),
  formulaPreview: document.querySelector("#formulaPreview"),
  waterAmount: document.querySelector("#waterAmount"),
  waterUnit: document.querySelector("#waterUnit"),
  solventAmount: document.querySelector("#solventAmount"),
  solventName: document.querySelector("#solventName"),
  catalystAmount: document.querySelector("#catalystAmount"),
  catalystName: document.querySelector("#catalystName"),
  temperature: document.querySelector("#temperature"),
  timeValue: document.querySelector("#timeValue"),
  pressure: document.querySelector("#pressure"),
  stirring: document.querySelector("#stirring"),
  ph: document.querySelector("#ph"),
  catalystRole: document.querySelector("#catalystRole"),
  analyzeButton: document.querySelector("#analyzeButton"),
  sampleButton: document.querySelector("#sampleButton"),
  exportPdf: document.querySelector("#exportPdf"),
  apiStatus: document.querySelector("#apiStatus"),
  modelStatus: document.querySelector("#modelStatus"),
  modelMessage: document.querySelector("#modelMessage"),
  modelStats: document.querySelector("#modelStats"),
  refreshModel: document.querySelector("#refreshModel"),
  trainModel: document.querySelector("#trainModel"),
  trainModelTop: document.querySelector("#trainModelTop"),
  trainingModelTag: document.querySelector("#trainingModelTag"),
  trainingModelMessage: document.querySelector("#trainingModelMessage"),
  trainingModelStats: document.querySelector("#trainingModelStats"),
  refreshNews: document.querySelector("#refreshNews"),
  newsList: document.querySelector("#newsList"),
  metricAlternatives: document.querySelector("#metricAlternatives"),
  metricValidation: document.querySelector("#metricValidation"),
  metricReview: document.querySelector("#metricReview"),
  resultStatus: document.querySelector("#resultStatus"),
  resultMessage: document.querySelector("#resultMessage"),
  compoundCount: document.querySelector("#compoundCount"),
  compoundList: document.querySelector("#compoundList"),
  environmentList: document.querySelector("#environmentList"),
  currentSolventTag: document.querySelector("#currentSolventTag"),
  currentAssessment: document.querySelector("#currentAssessment"),
  simulationTag: document.querySelector("#simulationTag"),
  simulationView: document.querySelector("#simulationView"),
  openVisualSimulation: document.querySelector("#openVisualSimulation"),
  closeVisualSimulation: document.querySelector("#closeVisualSimulation"),
  visualModal: document.querySelector("#visualModal"),
  simulationCanvas: document.querySelector("#simulationCanvas"),
  visualLegend: document.querySelector("#visualLegend"),
  alternativesCount: document.querySelector("#alternativesCount"),
  alternativesList: document.querySelector("#alternativesList"),
  toast: document.querySelector("#toast"),
};

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  analyzeFormula();
});

elements.sampleButton.addEventListener("click", () => {
  fillSampleFields();
  updatePreview();
  elements.solventName.focus();
});

elements.exportPdf.addEventListener("click", () => {
  exportPdfReport();
});

elements.refreshModel.addEventListener("click", () => {
  loadModelStatus();
});

elements.trainModel.addEventListener("click", () => {
  trainModel();
});

elements.trainModelTop.addEventListener("click", () => {
  trainModel();
});

elements.refreshNews.addEventListener("click", () => {
  loadNews();
});

document.querySelectorAll(".menu-btn").forEach((button) => {
  button.addEventListener("click", () => {
    switchView(button.getAttribute("data-view"));
  });
});

elements.openVisualSimulation.addEventListener("click", () => {
  openVisualSimulation();
});

elements.closeVisualSimulation.addEventListener("click", () => {
  closeVisualSimulation();
});

elements.visualModal.addEventListener("click", (event) => {
  if (event.target === elements.visualModal) {
    closeVisualSimulation();
  }
});

boot();

async function boot() {
  state.lang = localStorage.getItem("greenchem-lang") || "en";
  fillSampleFields();
  bindFieldPreview();
  bindLanguageSwitcher();
  applyLanguage();
  updatePreview();
  await Promise.all([checkHealth(), loadModelStatus()]);
  if (new URLSearchParams(window.location.search).get("demo") === "1") {
    await analyzeFormula();
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) {
      throw new Error("Health check failed");
    }
    setStatus(elements.apiStatus, "ok", "API online");
  } catch (error) {
    setStatus(elements.apiStatus, "error", "API unavailable");
    showToast(error.message || "API unavailable");
  }
}

async function loadModelStatus() {
  setStatus(elements.modelStatus, "idle", "Checking model");
  try {
    const data = await requestJson("/model/status");
    state.model = data;
    const label = data.available ? `Model ready: ${data.type || "available"}` : "Model not trained";
    setStatus(elements.modelStatus, data.available ? "ok" : "warn", label);
    elements.modelMessage.textContent = data.message || "No model details returned.";
    renderModelStats(data);
    elements.trainingModelTag.textContent = data.available ? "Available" : "Not trained";
    elements.trainingModelMessage.textContent = data.message || "No model details returned.";
  } catch (error) {
    setStatus(elements.modelStatus, "error", "Model check failed");
    elements.modelMessage.textContent = "Unable to read model status.";
    renderModelStats(null);
    elements.trainingModelTag.textContent = "Check failed";
    elements.trainingModelMessage.textContent = "Unable to read model status.";
  }
}

async function trainModel() {
  setBusy(elements.trainModel, true, "Training...");
  try {
    const data = await requestJson("/model/train", { method: "POST" });
    showToast(data.message || "Model training completed.");
    await loadModelStatus();
  } catch (error) {
    showToast(error.message || "Model training failed.");
  } finally {
    setBusy(elements.trainModel, false, "Train compatibility model");
  }
}

async function analyzeFormula() {
  const formulaText = buildFormulaText();
  if (!formulaText) {
    showToast(t("toast.needInput"));
    return;
  }

  setBusy(elements.analyzeButton, true, "Analyzing...");
  try {
    const data = await requestJson("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ formula_text: formulaText }),
    });
    state.analysis = data;
    renderAnalysis(data);
    showToast(t("toast.analysisComplete"));
  } catch (error) {
    showToast(error.message || "Analysis failed.");
  } finally {
    setBusy(elements.analyzeButton, false, "Analyze");
  }
}

async function exportPdfReport() {
  const formulaText = buildFormulaText();
  if (!formulaText) {
    showToast(t("toast.needPdfInput"));
    return;
  }

  setBusy(elements.exportPdf, true, "Exporting...");
  try {
    const response = await fetch("/analyze/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ formula_text: formulaText }),
    });

    if (!response.ok) {
      throw new Error(`PDF export failed with ${response.status}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "greenchem-analysis-report.pdf";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showToast(t("toast.pdfExported"));
  } catch (error) {
    showToast(error.message || "PDF export failed.");
  } finally {
    setBusy(elements.exportPdf, false, "Export PDF");
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.text();
  let data = null;
  if (body) {
    try {
      data = JSON.parse(body);
    } catch {
      data = body;
    }
  }

  if (!response.ok) {
    const message = data && data.detail ? data.detail : `Request failed with ${response.status}`;
    throw new Error(message);
  }
  return data;
}

function renderAnalysis(data) {
  elements.metricAlternatives.textContent = String(data.alternatives_found || 0);
  elements.metricValidation.textContent = data.validation_status || "Unknown";
  elements.metricReview.textContent = data.human_validation_required ? "Required" : "Optional";
  elements.resultStatus.textContent = data.status || "Analysis complete";
  elements.resultMessage.textContent = data.message || "Review the generated solvent replacement assessment.";

  renderDetectedInput(data.detected_input || {});
  renderCurrentAssessment(data.current_formula || {});
  renderSimulation(data, data.alternatives && data.alternatives[0]);
  renderAlternatives(data.alternatives || []);
}

function renderModelStats(data) {
  const accuracy = data && data.accuracy_percent !== null && data.accuracy_percent !== undefined
    ? `${data.accuracy_percent}%`
    : "--";
  const rows = data && data.training_rows ? data.training_rows.toLocaleString() : "--";
  const features = data && data.feature_count ? data.feature_count : "--";
  const source = data && data.label_source ? data.label_source : "--";

  elements.modelStats.innerHTML = `
    <span>Accuracy: ${escapeHtml(accuracy)}</span>
    <span>Rows: ${escapeHtml(rows)}</span>
  `;
  elements.trainingModelStats.innerHTML = `
    <span>Accuracy: ${escapeHtml(accuracy)}</span>
    <span>Training rows: ${escapeHtml(rows)}</span>
    <span>Features: ${escapeHtml(features)}</span>
    <span>Label source: ${escapeHtml(source)}</span>
  `;
}

function switchView(viewId) {
  document.querySelectorAll(".menu-btn").forEach((button) => {
    button.classList.toggle("active", button.getAttribute("data-view") === viewId);
  });
  document.querySelectorAll(".view-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === viewId);
  });
  if (viewId === "newsView") {
    loadNews();
  }
  if (viewId === "trainingView") {
    loadModelStatus();
  }
}

async function loadNews() {
  elements.newsList.innerHTML = `
    <div class="empty-state large">
      <strong>${escapeHtml(t("loading.news"))}</strong>
      <span>${escapeHtml(t("loading.newsBody"))}</span>
    </div>
  `;
  try {
    const data = await requestJson("/news");
    const items = data.items || [];
    if (!items.length) {
      throw new Error("No news items returned.");
    }
    elements.newsList.innerHTML = items.map((item) => `
      <article class="news-card">
        <div class="subtle">${escapeHtml(item.source || "Chemistry source")}</div>
        <a href="${escapeHtml(item.url || "#")}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || "Untitled news item")}</a>
        <p>${escapeHtml(item.summary || "Open the source for details.")}</p>
      </article>
    `).join("");
  } catch (error) {
    elements.newsList.innerHTML = `
      <div class="empty-state large">
        <strong>Could not load live news</strong>
        <span>${escapeHtml(error.message || "Please try again later.")}</span>
      </div>
    `;
  }
}

function renderDetectedInput(detected) {
  const compounds = detected.compounds || [];
  elements.compoundCount.textContent = `${compounds.length} ${compounds.length === 1 ? "compound" : "compounds"}`;

  if (!compounds.length) {
    elements.compoundList.className = "empty-state";
    elements.compoundList.textContent = "No compounds parsed.";
  } else {
    elements.compoundList.className = "compound-list";
    elements.compoundList.innerHTML = compounds.map((compound) => `
      <div class="compound-row">
        <div>
          <div class="label">${escapeHtml([compound.quantity, compound.unit].filter(Boolean).join(" ") || "Amount")}</div>
          <div class="subtle">${escapeHtml(compound.role || "compound")}</div>
        </div>
        <div class="value">
          <strong>${escapeHtml(compound.name || "Unnamed")}</strong>
          <div class="subtle">${escapeHtml(compound.formula || "No formula parsed")}</div>
        </div>
      </div>
    `).join("");
  }

  const environment = detected.environment || {};
  const filled = Object.entries(environment).filter(([, value]) => value);
  elements.environmentList.innerHTML = filled.length
    ? filled.map(([key, value]) => `<span class="chip"><strong>${formatKey(key)}</strong>${escapeHtml(value)}</span>`).join("")
    : `<span class="chip">No environment fields parsed</span>`;
}

function renderCurrentAssessment(current) {
  const solvent = current.solvent;
  elements.currentSolventTag.textContent = solvent ? solvent.name : "No solvent";

  if (!solvent && !current.catalyst_formula) {
    elements.currentAssessment.className = "empty-state";
    elements.currentAssessment.textContent = "No current formula assessment returned.";
    return;
  }

  elements.currentAssessment.className = "assessment-card";
  elements.currentAssessment.innerHTML = `
    <div class="assessment-head">
      <div>
        <strong>${escapeHtml(solvent ? solvent.name : "Unknown solvent")}</strong>
        <div class="subtle">${escapeHtml(solvent && solvent.formula ? solvent.formula : "Formula unavailable")}</div>
      </div>
      ${colorBadge(solvent ? solvent.chem21_color : "unknown")}
    </div>
    <div class="detail-grid">
      ${detail("Boiling point", solvent && solvent.boiling_point_c !== null ? `${solvent.boiling_point_c} C` : "Unknown")}
      ${detail("Catalyst", current.catalyst_formula || "Unknown")}
      ${detail("Role", current.catalyst_role || "Unknown")}
    </div>
    ${listBlock("Hazard summary", current.hazard_summary)}
    ${listBlock("Compatibility warnings", current.compatibility_warnings)}
  `;
}

function renderAlternatives(alternatives) {
  elements.alternativesCount.textContent = alternatives.length
    ? `${alternatives.length} result${alternatives.length === 1 ? "" : "s"}`
    : "No results";

  if (!alternatives.length) {
    elements.alternativesList.innerHTML = `
      <div class="empty-state large">
        <strong>No compatible alternatives returned</strong>
        <span>The backend did not find a candidate that passed its current knowledge-base and compatibility checks.</span>
      </div>
    `;
    return;
  }

  elements.alternativesList.innerHTML = alternatives.map((alternative) => {
    const solvent = alternative.replacement_solvent || {};
    return `
      <article class="alternative-card">
        <div class="alternative-head">
          <div>
            <strong>#${alternative.rank} ${escapeHtml(solvent.name || "Unknown solvent")}</strong>
            <div class="subtle">${escapeHtml(solvent.formula || "Formula unavailable")}</div>
          </div>
          <div class="badge-stack">
            ${colorBadge(solvent.chem21_color || "unknown")}
            ${statusBadge(alternative.validation_status)}
            <button class="simulate-btn" type="button" data-rank="${escapeHtml(alternative.rank)}">Simulate</button>
          </div>
        </div>
        <div class="detail-grid">
          ${detail("Status", alternative.status || "Unknown")}
          ${detail("Boiling point", solvent.boiling_point_c !== null && solvent.boiling_point_c !== undefined ? `${solvent.boiling_point_c} C` : "Unknown")}
          ${detail("GHS codes", solvent.ghs_codes && solvent.ghs_codes.length ? solvent.ghs_codes.join(", ") : "None in KB")}
        </div>
        ${formulaBlock(alternative.formula)}
        ${listBlock("Compatibility notes", alternative.compatibility_notes)}
        ${listBlock("Qualitative benefits", alternative.qualitative_benefits)}
        ${evidenceBlock(alternative.evidence)}
      </article>
    `;
  }).join("");

  elements.alternativesList.querySelectorAll("[data-rank]").forEach((button) => {
    button.addEventListener("click", () => {
      const rank = Number(button.getAttribute("data-rank"));
      const selected = alternatives.find((alternative) => Number(alternative.rank) === rank);
      renderSimulation(state.analysis, selected);
      document.querySelector(".simulation-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function renderSimulation(data, alternative) {
  if (!data || !alternative) {
    elements.simulationTag.textContent = "No simulation";
    elements.simulationView.className = "empty-state large";
    elements.simulationView.innerHTML = `
      <strong>No compatible alternative to simulate</strong>
      <span>The backend needs a valid recommendation before this comparison can be shown.</span>
    `;
    return;
  }

  const current = data.current_formula || {};
  const currentSolvent = current.solvent || {};
  const replacement = alternative.replacement_solvent || {};
  const currentLines = buildCurrentFormulaLines(data.detected_input || {});
  const replacementLines = alternative.formula || [];
  const currentColor = currentSolvent.chem21_color || "unknown";
  const replacementColor = replacement.chem21_color || "unknown";

  state.simulatedAlternative = alternative;
  elements.simulationTag.textContent = `Testing #${alternative.rank}`;
  elements.simulationView.className = "simulation-view";
  elements.simulationView.innerHTML = `
    <div class="simulation-summary">
      ${simulationCard("Current process", currentSolvent.name || "Unknown solvent", currentSolvent.formula || "Unknown", currentColor, currentSolvent.ghs_codes, currentLines)}
      <div class="simulation-arrow" aria-hidden="true">-></div>
      ${simulationCard("Suggested test", replacement.name || "Unknown solvent", replacement.formula || "Unknown", replacementColor, replacement.ghs_codes, replacementLines)}
    </div>
    <div class="change-list">
      <div class="change-item">
        <strong>Main change</strong>
        <span>${escapeHtml(currentSolvent.name || "Current solvent")} -> ${escapeHtml(replacement.name || "Replacement solvent")}</span>
      </div>
      <div class="change-item">
        <strong>Guide color</strong>
        <span>${escapeHtml(currentColor)} -> ${escapeHtml(replacementColor)}</span>
      </div>
      <div class="change-item">
        <strong>Meaning</strong>
        <span>This is a visual decision simulation. It shows what to test next, not a guaranteed lab result.</span>
      </div>
      <div class="change-item">
        <strong>Validation</strong>
        <span>${escapeHtml(alternative.validation_status || "Human validation required")}</span>
      </div>
    </div>
    ${listBlock("Why this candidate appears", alternative.qualitative_benefits)}
  `;
}

function simulationCard(title, name, formula, color, ghsCodes, lines) {
  return `
    <div class="simulation-card">
      <div class="simulation-head">
        <div>
          <div class="label">${escapeHtml(title)}</div>
          <strong>${escapeHtml(name)}</strong>
          <div class="subtle">${escapeHtml(formula)}</div>
        </div>
        ${colorBadge(color)}
      </div>
      ${riskMeter(color)}
      <div class="detail-grid">
        ${detail("GHS codes", ghsCodes && ghsCodes.length ? ghsCodes.join(", ") : "None in KB")}
        ${detail("Guide color", color || "unknown")}
        ${detail("Action", title === "Current process" ? "Baseline" : "Candidate to test")}
      </div>
      ${formulaBlock(lines)}
    </div>
  `;
}

function riskMeter(color) {
  const normalized = String(color || "unknown").toLowerCase();
  const active = normalized === "green" ? 1 : normalized === "yellow" ? 2 : normalized === "red" ? 3 : 0;
  const classes = ["active-green", "active-yellow", "active-red"];
  return `
    <div class="risk-meter">
      <div class="label">Relative guide concern</div>
      <div class="risk-track">
        ${[1, 2, 3].map((index) => `<span class="risk-step ${active >= index ? classes[index - 1] : ""}"></span>`).join("")}
      </div>
    </div>
  `;
}

function buildCurrentFormulaLines(detected) {
  const compounds = detected.compounds || [];
  if (!compounds.length) {
    return [buildFormulaText().split("\n")[0] || "No current formula parsed."];
  }
  return compounds.map((compound) => {
    return [compound.quantity, compound.unit, compound.name].filter(Boolean).join(" ");
  });
}

function detail(label, value) {
  return `
    <div class="detail">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `;
}

function listBlock(title, items) {
  const list = Array.isArray(items) ? items.filter(Boolean) : [];
  if (!list.length) {
    return `
      <div class="list-block">
        <strong>${escapeHtml(title)}</strong>
        <div class="subtle">None returned.</div>
      </div>
    `;
  }

  return `
    <div class="list-block">
      <strong>${escapeHtml(title)}</strong>
      <ul>${list.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
}

function evidenceBlock(items) {
  const evidence = Array.isArray(items) ? items.filter(Boolean) : [];
  if (!evidence.length) {
    return listBlock("Evidence", []);
  }

  return `
    <div class="list-block">
      <strong>Evidence</strong>
      <ul>
        ${evidence.map((item) => `
          <li><strong>${escapeHtml(item.source || "Source")}:</strong> ${escapeHtml(item.statement || "")}</li>
        `).join("")}
      </ul>
    </div>
  `;
}

function formulaBlock(lines) {
  const formula = Array.isArray(lines) ? lines.filter(Boolean) : [];
  if (!formula.length) {
    return "";
  }
  return `
    <div class="formula-lines">
      ${formula.map((line) => `<span>${escapeHtml(line)}</span>`).join("")}
    </div>
  `;
}

function colorBadge(color) {
  const normalized = String(color || "unknown").toLowerCase();
  const label = normalized === "green" ? "CHEM21 green"
    : normalized === "yellow" ? "CHEM21 yellow"
    : normalized === "red" ? "CHEM21 red"
    : "CHEM21 unknown";
  return `<span class="badge badge-${escapeHtml(normalized)}">${escapeHtml(label)}</span>`;
}

function statusBadge(status) {
  const normalized = String(status || "Unknown");
  const className = normalized.includes("Published")
    ? "badge-green"
    : normalized.includes("uncertain") || normalized.includes("Experimental")
      ? "badge-yellow"
      : "badge-blue";
  return `<span class="badge ${className}">${escapeHtml(normalized)}</span>`;
}

function setStatus(target, type, text) {
  const dotClass = type === "ok" ? "dot-ok" : type === "warn" ? "dot-warn" : type === "error" ? "dot-error" : "dot-idle";
  target.innerHTML = `<span class="dot ${dotClass}"></span><span>${escapeHtml(text)}</span>`;
}

function setBusy(button, isBusy, label) {
  button.disabled = isBusy;
  button.textContent = label;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 3600);
}

function formatKey(key) {
  return `${String(key).replaceAll("_", " ")}:`;
}

function bindFieldPreview() {
  getInputFields().forEach((field) => {
    field.addEventListener("input", updatePreview);
    field.addEventListener("change", updatePreview);
  });
}

function getInputFields() {
  return [
    elements.waterAmount,
    elements.waterUnit,
    elements.solventAmount,
    elements.solventName,
    elements.catalystAmount,
    elements.catalystName,
    elements.temperature,
    elements.timeValue,
    elements.pressure,
    elements.stirring,
    elements.ph,
    elements.catalystRole,
  ];
}

function fillSampleFields() {
  elements.waterAmount.value = "20";
  elements.waterUnit.value = "mL";
  elements.solventAmount.value = "10";
  elements.solventName.value = "Acetone";
  elements.catalystAmount.value = "1";
  elements.catalystName.value = "H2SO4";
  elements.temperature.value = "90C";
  elements.timeValue.value = "4h";
  elements.pressure.value = "1 atm";
  elements.stirring.value = "300 rpm";
  elements.ph.value = "2";
  elements.catalystRole.value = "acid_catalyst";
}

function buildFormulaText() {
  const lines = [];
  const waterLine = joinParts(elements.waterAmount.value, elements.waterUnit.value, "H2O");
  const solventLine = joinParts(elements.solventAmount.value, "mL", elements.solventName.value);
  const catalystLine = joinParts(elements.catalystAmount.value, "mL", elements.catalystName.value);

  if (waterLine) lines.push(waterLine);
  if (solventLine) lines.push(solventLine);
  if (catalystLine) lines.push(catalystLine);

  addField(lines, "Temperature", elements.temperature.value);
  addField(lines, "Time", elements.timeValue.value);
  addField(lines, "Pressure", elements.pressure.value);
  addField(lines, "Stirring", elements.stirring.value);
  addField(lines, "pH", elements.ph.value);
  addField(lines, "Solvent", elements.solventName.value);
  addField(lines, "Catalyst", elements.catalystName.value);
  addField(lines, "Catalyst role", elements.catalystRole.value);

  return lines.join("\n").trim();
}

function joinParts(...parts) {
  return parts.map((part) => String(part || "").trim()).filter(Boolean).join(" ");
}

function addField(lines, label, value) {
  const cleanValue = String(value || "").trim();
  if (cleanValue) {
    lines.push(`${label}: ${cleanValue}`);
  }
}

function updatePreview() {
  elements.formulaPreview.textContent = buildFormulaText();
}

function openVisualSimulation() {
  if (!state.analysis || !state.simulatedAlternative) {
    showToast(t("toast.needSimulation"));
    return;
  }

  elements.visualModal.classList.add("open");
  elements.visualModal.setAttribute("aria-hidden", "false");
  buildVisualLegend();
  resetParticles();
  startVisualAnimation();
}

function closeVisualSimulation() {
  elements.visualModal.classList.remove("open");
  elements.visualModal.setAttribute("aria-hidden", "true");
  if (state.animationFrame) {
    cancelAnimationFrame(state.animationFrame);
    state.animationFrame = null;
  }
}

function buildVisualLegend() {
  const current = state.analysis.current_formula || {};
  const currentSolvent = current.solvent || {};
  const replacement = state.simulatedAlternative.replacement_solvent || {};
  elements.visualLegend.innerHTML = `
    <span class="legend-item"><span class="legend-dot" style="background:#a67812"></span>${escapeHtml(currentSolvent.name || "Current solvent")}</span>
    <span class="legend-item"><span class="legend-dot" style="background:#168658"></span>${escapeHtml(replacement.name || "Replacement solvent")}</span>
    <span class="legend-item"><span class="legend-dot" style="background:#246b91"></span>Water / medium</span>
    <span class="legend-item"><span class="legend-dot" style="background:#b94a48"></span>Catalyst</span>
  `;
}

function resetParticles() {
  const canvas = elements.simulationCanvas;
  const width = canvas.width;
  const height = canvas.height;
  state.particles = [];

  addParticles("current", 28, width * 0.25, height * 0.52, 155, "#a67812");
  addParticles("replacement", 28, width * 0.75, height * 0.52, 155, "#168658");
  addParticles("water-left", 14, width * 0.25, height * 0.52, 135, "#246b91");
  addParticles("water-right", 14, width * 0.75, height * 0.52, 135, "#246b91");
  addParticles("catalyst-left", 5, width * 0.25, height * 0.52, 85, "#b94a48");
  addParticles("catalyst-right", 5, width * 0.75, height * 0.52, 85, "#b94a48");
}

function addParticles(group, count, centerX, centerY, radius, color) {
  for (let index = 0; index < count; index += 1) {
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * radius;
    state.particles.push({
      group,
      color,
      x: centerX + Math.cos(angle) * distance,
      y: centerY + Math.sin(angle) * distance * 0.65,
      z: Math.random() * 80,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.5,
      size: 4 + Math.random() * 5,
      centerX,
      centerY,
      radius,
    });
  }
}

function startVisualAnimation() {
  const canvas = elements.simulationCanvas;
  const ctx = canvas.getContext("2d");
  const current = state.analysis.current_formula || {};
  const currentSolvent = current.solvent || {};
  const replacement = state.simulatedAlternative.replacement_solvent || {};

  const draw = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawVisualBackground(ctx, canvas, currentSolvent, replacement);
    updateAndDrawParticles(ctx);
    state.animationFrame = requestAnimationFrame(draw);
  };
  draw();
}

function drawVisualBackground(ctx, canvas, currentSolvent, replacement) {
  ctx.fillStyle = "#eef3f1";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawBeaker(ctx, 130, 95, 300, 330, "Current process", currentSolvent.name || "Current solvent", currentSolvent.chem21_color || "unknown");
  drawBeaker(ctx, 670, 95, 300, 330, "Suggested test", replacement.name || "Replacement solvent", replacement.chem21_color || "unknown");

  ctx.fillStyle = "#168658";
  ctx.font = "bold 34px Segoe UI, Arial";
  ctx.fillText("->", 525, 275);

  ctx.fillStyle = "#60716b";
  ctx.font = "15px Segoe UI, Arial";
  ctx.fillText("Same process context, different solvent candidate", 382, 455);
}

function drawBeaker(ctx, x, y, width, height, title, solvent, color) {
  ctx.fillStyle = "#fbfcfb";
  ctx.strokeStyle = "#d7e1dc";
  ctx.lineWidth = 2;
  roundRect(ctx, x, y, width, height, 8);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = color === "green" ? "rgba(22,134,88,0.16)" : color === "red" ? "rgba(185,74,72,0.15)" : "rgba(166,120,18,0.16)";
  roundRect(ctx, x + 28, y + 105, width - 56, height - 145, 8);
  ctx.fill();

  ctx.fillStyle = "#17211d";
  ctx.font = "bold 18px Segoe UI, Arial";
  ctx.fillText(title, x + 24, y + 34);
  ctx.font = "bold 24px Segoe UI, Arial";
  ctx.fillText(solvent, x + 24, y + 66);

  ctx.fillStyle = color === "green" ? "#168658" : color === "red" ? "#b94a48" : "#a67812";
  ctx.font = "bold 14px Segoe UI, Arial";
  ctx.fillText(`CHEM21 ${color}`, x + 24, y + height - 24);
}

function updateAndDrawParticles(ctx) {
  for (const particle of state.particles) {
    particle.x += particle.vx;
    particle.y += particle.vy + Math.sin(Date.now() / 600 + particle.z) * 0.02;

    const dx = particle.x - particle.centerX;
    const dy = (particle.y - particle.centerY) / 0.65;
    if (Math.sqrt(dx * dx + dy * dy) > particle.radius) {
      particle.vx *= -1;
      particle.vy *= -1;
    }

    const depthScale = 0.75 + particle.z / 240;
    ctx.beginPath();
    ctx.fillStyle = particle.color;
    ctx.globalAlpha = 0.72 + particle.z / 300;
    ctx.arc(particle.x, particle.y, particle.size * depthScale, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}

function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + width, y, x + width, y + height, radius);
  ctx.arcTo(x + width, y + height, x, y + height, radius);
  ctx.arcTo(x, y + height, x, y, radius);
  ctx.arcTo(x, y, x + width, y, radius);
  ctx.closePath();
}

function bindLanguageSwitcher() {
  document.querySelectorAll(".lang-btn").forEach((button) => {
    button.addEventListener("click", () => {
      state.lang = button.getAttribute("data-lang") || "en";
      localStorage.setItem("greenchem-lang", state.lang);
      applyLanguage();
      if (state.analysis) {
        renderAnalysis(state.analysis);
      }
    });
  });
}

function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.getAttribute("data-i18n"));
  });
  document.querySelectorAll(".lang-btn").forEach((button) => {
    button.classList.toggle("active", button.getAttribute("data-lang") === state.lang);
  });

  setText(".brand h1", "brand.title");
  setText(".field-section:nth-of-type(1) .field-section-title", "section.formula");
  setText(".field-section:nth-of-type(2) .field-section-title", "section.conditions");
  setLabel(elements.waterAmount, "field.waterAmount");
  setLabel(elements.waterUnit, "field.unit");
  setLabel(elements.solventAmount, "field.solventAmount");
  setLabel(elements.solventName, "field.solvent");
  setLabel(elements.catalystAmount, "field.catalystAmount");
  setLabel(elements.catalystName, "field.catalyst");
  setLabel(elements.temperature, "field.temperature");
  setLabel(elements.timeValue, "field.time");
  setLabel(elements.pressure, "field.pressure");
  setLabel(elements.stirring, "field.stirring");
  setLabel(elements.ph, "field.ph");
  setLabel(elements.catalystRole, "field.catalystRole");
  elements.analyzeButton.textContent = t("action.analyze");
  elements.sampleButton.textContent = t("action.sample");
  elements.exportPdf.textContent = t("action.exportPdf");
  elements.trainModel.textContent = t("action.train");
  elements.trainModelTop.textContent = t("action.train");
  elements.refreshNews.textContent = t("action.refreshNews");
  elements.openVisualSimulation.textContent = t("action.view3d");
  document.querySelector("#metricAlternatives + small").textContent = t("metric.alternatives");
  document.querySelector("#metricValidation + small").textContent = t("metric.validation");
  document.querySelector("#metricReview + small").textContent = t("metric.review");
  if (!state.analysis) {
    elements.resultStatus.textContent = t("hero.ready");
    elements.resultMessage.textContent = t("hero.readyMessage");
  }
  document.querySelector(".ai-notice").textContent = t("notice.ai");
  setText(".grid.two-col .section-panel:nth-child(1) h3", "detected.title");
  setText(".grid.two-col .section-panel:nth-child(2) h3", "assessment.title");
  setText(".simulation-panel h3", "simulation.title");
  setText(".alternatives-panel h3", "alternatives.title");
  setText("#newsView h3", "news.title");
  setText(".news-intro", "news.intro");
  setText("#trainingView .section-heading h3", "training.title");
  setText(".training-card:nth-child(1) h3", "training.when");
  setText(".training-card:nth-child(1) p:nth-of-type(1)", "training.whenBody");
  setText(".training-card:nth-child(1) p:nth-of-type(2)", "training.whenBody2");
  setText(".training-card:nth-child(2) h3", "training.current");
  setText(".training-card:nth-child(3) h3", "training.human");
  setText(".training-card:nth-child(3) p", "training.humanBody");
}

function t(key) {
  return (translations[state.lang] && translations[state.lang][key]) || translations.en[key] || key;
}

function setText(selector, key) {
  const node = document.querySelector(selector);
  if (node) node.textContent = t(key);
}

function setLabel(input, key) {
  const label = input && input.closest("label");
  if (!label) return;
  const textNode = Array.from(label.childNodes).find((node) => node.nodeType === Node.TEXT_NODE);
  if (textNode) {
    textNode.textContent = `\n                ${t(key)}\n                `;
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
