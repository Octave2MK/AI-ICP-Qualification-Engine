const API_BASE = "/api";
const COOLDOWN_SECONDS = 30;
const MAX_RUNS_PER_SESSION = 20;
const POLL_INTERVAL_MS = 1500;

let lastRunAt = 0;
let runCount = 0;
let currentProspects = [];

const LOADER_MIN_DISPLAY_MS = 400;
const LOADER_RETRY_DELAY_MS = 1000;

window.addEventListener("load", () => {
  initializeEnvironment();
});

async function initializeEnvironment() {
  const loader = document.getElementById("page-loader");
  const loaderStatus = document.getElementById("page-loader-status");
  const app = document.getElementById("app-container");

  const startedAt = Date.now();
  await waitForApiReady(loaderStatus);

  const elapsed = Date.now() - startedAt;
  if (elapsed < LOADER_MIN_DISPLAY_MS) {
    await sleep(LOADER_MIN_DISPLAY_MS - elapsed);
  }

  loader.style.opacity = "0";
  loader.style.visibility = "hidden";
  app.classList.remove("hidden");
}

async function waitForApiReady(loaderStatus) {
  let attempt = 0;

  for (;;) {
    attempt += 1;
    try {
      const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
      if (res.ok) {
        if (loaderStatus) loaderStatus.textContent = "Environnement prêt.";
        return;
      }
      throw new Error(`health check returned ${res.status}`);
    } catch (err) {
      if (loaderStatus) {
        loaderStatus.textContent =
          attempt === 1
            ? "Connexion au serveur..."
            : `Serveur indisponible, nouvelle tentative (${attempt})...`;
      }
      console.warn("API health check failed:", err);
      await sleep(LOADER_RETRY_DELAY_MS);
    }
  }
}

async function createJob(payload) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Échec de création du job (${res.status})`);
  return (await res.json()).job_id;
}

async function getStatus(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error(`Échec de la vérification du statut (${res.status})`);
  return res.json();
}

async function getResults(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/results`);
  if (!res.ok) throw new Error(`Échec de la récupération des résultats (${res.status})`);
  return res.json();
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function splitKeywords(raw) {
  return String(raw || "").split(",").map((value) => value.trim()).filter(Boolean);
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}

function toggleVisibility(id, forceHide) {
  const el = document.getElementById(id);
  if (forceHide) {
    el.classList.add("hidden");
  } else {
    el.classList.remove("hidden");
  }
}

function showMessage(type, message) {
  const id = type === "warning" ? "cooldown-warning" : "error-message";
  const el = document.getElementById(id);
  el.textContent = message;
  toggleVisibility(id, false);
}

function renderResults(prospects) {
  currentProspects = Array.isArray(prospects) ? prospects : [];
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";

  currentProspects.forEach((prospect, index) => {
    const row = document.createElement("tr");
    row.className = "row-animate";
    row.style.animationDelay = `${index * 0.05}s`;

    row.innerHTML = `
      <td><strong>${escapeHtml(prospect.name)}</strong></td>
      <td><a href="${escapeHtml(prospect.linkedin_url)}" target="_blank" rel="noopener">Lien Profil ↗</a></td>
      <td>${escapeHtml(prospect.job_title)}</td>
      <td><span class="status-badge">${escapeHtml(prospect.status ?? "N/A")}</span></td>
      <td class="text-muted">${escapeHtml(prospect.error ?? "-")}</td>
    `;
    tbody.appendChild(row);
  });

  document.getElementById("results-count").textContent = `${currentProspects.length} entrées qualifiées`;
  document.getElementById("export-csv-btn").disabled = currentProspects.length === 0;
  toggleVisibility("results-section", false);
}

/* --- Export CSV --- */
function csvCell(value) {
  const str = String(value ?? "");
  return `"${str.replace(/"/g, '""')}"`;
}

function exportCsv() {
  if (!currentProspects.length) return;

  const headers = ["Identité", "Profil LinkedIn", "Fonction", "Statut", "Log Erreur"];
  const lines = [headers.map(csvCell).join(",")];

  currentProspects.forEach((p) => {
    lines.push([
      csvCell(p.name),
      csvCell(p.linkedin_url),
      csvCell(p.job_title),
      csvCell(p.status ?? "N/A"),
      csvCell(p.error ?? "-"),
    ].join(","));
  });

  const blob = new Blob(["\uFEFF" + lines.join("\r\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  link.href = url;
  link.download = `icp-prospects-${stamp}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function handleSubmit(event) {
  event.preventDefault();

  const now = Date.now();
  const remainingCooldown = COOLDOWN_SECONDS - (now - lastRunAt) / 1000;

  toggleVisibility("cooldown-warning", true);
  toggleVisibility("error-message", true);

  if (lastRunAt && remainingCooldown > 0) {
    showMessage("warning", `Protection anti-spam active. Patientez ${Math.ceil(remainingCooldown)}s.`);
    return;
  }

  if (runCount >= MAX_RUNS_PER_SESSION) {
    showMessage("warning", `Quota de session atteint (${MAX_RUNS_PER_SESSION}). Veuillez recharger l'environnement.`);
    return;
  }

  lastRunAt = now;
  runCount += 1;

  const formData = new FormData(event.target);
  const payload = {
    job_title: formData.get("job_title").trim(),
    country: formData.get("country").trim(),
    sector: String(formData.get("sector") || "").trim(),
    max_prospects: Number(formData.get("max_prospects")),
    required_keywords: splitKeywords(formData.get("required_keywords")),
    forbidden_keywords: splitKeywords(formData.get("forbidden_keywords")),
  };

  toggleVisibility("results-section", true);
  toggleVisibility("progress-section", false);

  const progressBar = document.getElementById("progress-bar");
  const progressPercent = document.getElementById("progress-percent");
  const progressText = document.getElementById("progress-text");

  progressBar.style.width = "0%";
  progressPercent.textContent = "0%";
  progressText.textContent = "Initialisation du cluster d'extraction...";

  const submitButton = document.getElementById("submit-btn");
  const btnText = submitButton.querySelector(".btn-text");
  const btnSpinner = submitButton.querySelector(".btn-spinner");

  submitButton.disabled = true;
  btnText.textContent = "Exécution...";
  btnSpinner.classList.remove("hidden");

  try {
    const jobId = await createJob(payload);

    let status;
    do {
      await sleep(POLL_INTERVAL_MS);
      status = await getStatus(jobId);

      const percentStr = `${status.progress_percent || 0}%`;
      progressBar.style.width = percentStr;
      progressPercent.textContent = percentStr;
      progressText.textContent = status.progress_text || "Traitement des nœuds...";
    } while (status.status === "pending" || status.status === "running");

    toggleVisibility("progress-section", true);

    if (status.status === "failed") {
      showMessage("error", status.error || "Erreur système lors du traitement. Consultez les logs serveur.");
      return;
    }

    const { prospects } = await getResults(jobId);
    renderResults(prospects);
  } catch (err) {
    toggleVisibility("progress-section", true);
    showMessage("error", "Exception non gérée durant l'exécution de la requête.");
    console.error(err);
  } finally {
    submitButton.disabled = false;
    btnText.textContent = "Lancer la recherche";
    btnSpinner.classList.add("hidden");
  }
}

document.getElementById("icp-form").addEventListener("submit", handleSubmit);
document.getElementById("export-csv-btn").addEventListener("click", exportCsv);