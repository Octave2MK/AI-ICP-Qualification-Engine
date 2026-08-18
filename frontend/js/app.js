const API_BASE = "/api";
const COOLDOWN_SECONDS = 30;
const MAX_RUNS_PER_SESSION = 20;
const POLL_INTERVAL_MS = 1500;

let lastRunAt = 0;
let runCount = 0;

async function createJob(payload) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`job creation failed (${res.status})`);
  }
  return (await res.json()).job_id;
}

async function getStatus(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error(`status check failed (${res.status})`);
  }
  return res.json();
}

async function getResults(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/results`);
  if (!res.ok) {
    throw new Error(`results fetch failed (${res.status})`);
  }
  return res.json();
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function splitKeywords(raw) {
  return raw
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}

function setHidden(id, hidden) {
  document.getElementById(id).hidden = hidden;
}

function showWarning(message) {
  const el = document.getElementById("cooldown-warning");
  el.textContent = message;
  el.hidden = false;
}

function showError(message) {
  const el = document.getElementById("error-message");
  el.textContent = message;
  el.hidden = false;
}

function renderResults(prospects) {
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";

  for (const prospect of prospects) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(prospect.name)}</td>
      <td><a href="${escapeHtml(prospect.linkedin_url)}" target="_blank" rel="noopener">${escapeHtml(prospect.linkedin_url)}</a></td>
      <td>${escapeHtml(prospect.job_title)}</td>
      <td>${escapeHtml(prospect.status ?? "")}</td>
      <td>${escapeHtml(prospect.error ?? "")}</td>
    `;
    tbody.appendChild(row);
  }

  document.getElementById("results-count").textContent =
    `${prospects.length} prospects traités`;
  setHidden("results-section", false);
}

async function handleSubmit(event) {
  event.preventDefault();

  const now = Date.now();
  const remainingCooldown = COOLDOWN_SECONDS - (now - lastRunAt) / 1000;

  setHidden("cooldown-warning", true);

  if (lastRunAt && remainingCooldown > 0) {
    showWarning(
      `Veuillez patienter encore ${Math.ceil(remainingCooldown)} s avant de relancer une recherche.`
    );
    return;
  }

  if (runCount >= MAX_RUNS_PER_SESSION) {
    showWarning(
      `Nombre maximal de recherches atteint pour cette session (${MAX_RUNS_PER_SESSION}). Rechargez la page pour réinitialiser.`
    );
    return;
  }

  lastRunAt = now;
  runCount += 1;

  const formData = new FormData(event.target);
  const payload = {
    job_title: formData.get("job_title").trim(),
    country: formData.get("country").trim(),
    sector: formData.get("sector").trim(),
    max_prospects: Number(formData.get("max_prospects")),
    required_keywords: splitKeywords(formData.get("required_keywords")),
    forbidden_keywords: splitKeywords(formData.get("forbidden_keywords")),
  };

  setHidden("error-message", true);
  setHidden("results-section", true);
  setHidden("progress-section", false);

  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  progressBar.value = 0;
  progressText.textContent = "Initialisation...";

  const submitButton = event.target.querySelector("button[type=submit]");
  submitButton.disabled = true;

  try {
    const jobId = await createJob(payload);

    let status;
    do {
      await sleep(POLL_INTERVAL_MS);
      status = await getStatus(jobId);
      progressBar.value = status.progress_percent;
      progressText.textContent = status.progress_text;
    } while (status.status === "pending" || status.status === "running");

    setHidden("progress-section", true);

    if (status.status === "failed") {
      showError(
        status.error ||
          "Une erreur est survenue pendant le traitement. Consultez les journaux serveur pour plus de détails."
      );
      return;
    }

    const { prospects } = await getResults(jobId);
    renderResults(prospects);
  } catch (err) {
    setHidden("progress-section", true);
    showError("Une erreur est survenue pendant le traitement.");
    console.error(err);
  } finally {
    submitButton.disabled = false;
  }
}

document.getElementById("icp-form").addEventListener("submit", handleSubmit);
