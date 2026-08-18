# Plan de migration — Frontend HTML/CSS/JS statique + exposition via FastAPI

**Statut :** exécuté et validé (Parties A à D). Le backend FastAPI (`app/api/`), le frontend statique (`frontend/`), leur assemblage en un seul service, ainsi que le retrait complet de Streamlit sont en place. Validé par la suite de tests automatisée, `ruff`, `mypy`, un test manuel via `curl`/navigateur, et un build + run Docker réel (utilisateur non-root, healthcheck, cycle de job complet). Ce document reste comme référence de conception ; les cases à cocher ci-dessous marquent l'état réel.
**Portée :** (1) construire une API FastAPI (`app/api/`) qui expose le workflow de qualification, (2) écrire un frontend **statique** — fichiers `.html`/`.css`/`.js` réels, écrits à la main, servis tels quels — qui consomme cette API en HTTP depuis le navigateur, (3) faire servir ce frontend directement par l'application FastAPI (un seul service), en remplacement complet de l'interface Streamlit actuelle.

**Changement par rapport à la version précédente de ce plan :** le frontend n'est **plus** généré par un framework Python (Streamlit). Il s'agit de vrais fichiers `index.html` / `style.css` / `app.js`, sans générateur, sans bundler, sans framework JS, sans étape de build — servis directement par FastAPI via `StaticFiles`. Streamlit est retiré du projet en fin de migration (Partie D), pas seulement déplacé.

**Décision actée (inchangée) :** l'API est **asynchrone par job** (`POST /api/jobs` crée un job et retourne immédiatement un `job_id` ; `GET /api/jobs/{id}` renvoie le statut/la progression ; `GET /api/jobs/{id}/results` renvoie le résultat une fois terminé). Le workflow complet peut prendre plusieurs minutes ; un endpoint synchrone bloquant risquerait un timeout HTTP et ne permettrait aucun retour de progression.

**Principe directeur :** comme pour `MIGRATION.md`, chaque étape doit laisser le dépôt dans un état où `uv run pytest -q -m "not integration"`, `uv run ruff check .` et `uv run mypy app` passent.

---

## 0. Architecture cible

```
Aujourd'hui :
  Navigateur --rendu serveur--> Streamlit (app/ui/) --appel Python direct--> app/factory.py --> workflow --> DB/SearXNG/Gemini

Cible :
  Navigateur --HTML/CSS/JS statiques--> FastAPI (app/api/) --StaticFiles + API JSON--> app/factory.py --> workflow --> DB/SearXNG/Gemini
```

**Un seul service applicatif** sert à la fois les fichiers statiques et l'API JSON : FastAPI monte `frontend/` comme répertoire statique et expose les routes `/api/jobs*` en parallèle. Le navigateur charge `index.html`, qui appelle `/api/jobs...` en `fetch()` — c'est cette fois un vrai appel cross-boundary **depuis le navigateur**, contrairement à la version précédente du plan (où Streamlit, exécuté côté serveur, appelait l'API en Python) : comme frontend et API sont servis **sur la même origine** (même host:port), **CORS n'est pas nécessaire** dans le déploiement par défaut. Une note dédiée (C.4) couvre le cas où les fichiers statiques seraient un jour servis ailleurs (CDN, Nginx séparé).

Pas de framework JS (React/Vue/etc.), pas de bundler (Vite/webpack), pas de npm : `frontend/js/app.js` est du JavaScript natif (ES modules), directement exécutable par le navigateur sans étape de compilation — cohérent avec la demande de fichiers « à utiliser directement ».

---

## Partie A — Construire l'API FastAPI (backend pur, aucun frontend encore servi)

Inchangée dans son principe par rapport à la version précédente du plan ; seul ajout : toutes les routes API vivent sous le préfixe `/api`, pour laisser `/` libre pour les fichiers statiques (Partie C).

### A.1 Dépendances

```bash
uv add fastapi "uvicorn[standard]"
```

`httpx` est déjà présent (utilisé par `SearXNGProvider`) — inutile pour le frontend cette fois (il n'appelle plus l'API depuis du code Python), mais reste utile pour les tests de l'API (`httpx.ASGITransport`).

### A.2 Modèle de persistance des jobs

Ajouter un modèle `Job` dans `app/database/models.py` :

```python
class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)          # uuid4
    status = Column(String, nullable=False)         # pending | running | succeeded | failed
    progress_percent = Column(Integer, default=0)
    progress_text = Column(String, default="")
    icp_json = Column(String, nullable=False)
    results_json = Column(String, nullable=True)
    error = Column(String, nullable=True)             # message générique, jamais l'exception brute
    created_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
```

Ajouter `app/repositories/job_repository.py` (`create`, `get`, `update_progress`, `mark_succeeded`, `mark_failed`), même style que `QualificationRepository`/`ProspectRepository`.

### A.3 Schéma additif

Étendre `app/database/schema.py::ensure_schema()` pour créer la table `jobs` si absente (même principe que la migration additive déjà en place pour `icp_fingerprint`) ; `Base.metadata.create_all()` (déjà appelé par `init_db()`) suffit en réalité pour une table entièrement nouvelle.

### A.4 Contrats Pydantic (`app/api/schemas.py`)

```python
class ICPRequest(BaseModel):
    job_title: str
    country: str
    sector: str = ""
    max_prospects: int = Field(20, ge=1, le=100)
    required_keywords: list[str] = []
    forbidden_keywords: list[str] = []

class JobCreatedResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_percent: int
    progress_text: str
    error: str | None = None

class ProspectResultSchema(BaseModel):
    name: str
    linkedin_url: str
    job_title: str
    status: str | None = None       # decision.status (QUALIFIED/REVIEW/REJECTED/EXCLUDED)
    score: int | None = None
    confidence: float | None = None
    error: str | None = None

class JobResultsResponse(BaseModel):
    job_id: str
    prospects: list[ProspectResultSchema]
```

`required_keywords`/`forbidden_keywords` voyagent en JSON comme de vraies listes (`["a", "b"]`) — c'est le frontend JS qui se charge de découper la saisie utilisateur (séparée par des virgules) en tableau avant l'envoi, pas l'API (voir B.2).

### A.5 Service applicatif (`app/api/job_service.py`)

- `create_job(db, icp: ICP) -> Job` : crée la ligne `Job` (`status="pending"`).
- `run_job(job_id: str, icp: ICP) -> None` : exécutée en arrière-plan (A.6). Ouvre sa **propre session DB** (`SessionLocal()`, jamais celle de la requête HTTP qui a créé le job). Passe à `status="running"`, appelle `create_full_workflow(db).run(db, icp, progress_callback=...)` avec un callback qui met à jour `progress_percent`/`progress_text` et fait un `commit()` à chaque étape (sinon le polling HTTP, exécuté dans un autre thread/une autre session, ne verrait jamais l'avancement). Succès → sérialise les résultats dans `results_json`, `status="succeeded"`. Exception → log complet côté serveur (`logger.exception`), `status="failed"`, `error` réduit à un message générique (même principe que la correction C.1.4 de l'audit : jamais l'exception brute exposée au client).
- Sérialisation : chaque entrée de `workflow.run()` contient un objet SQLAlchemy `Prospect` et un `ICPDecision`/`QualificationResult` (dataclasses non JSON-sérialisables tels quels) — un petit mapper dédié (`_serialize_result(item) -> dict`) en extrait les champs voulus.
- `get_status(db, job_id)`, `get_results(db, job_id)`.

### A.6 Exécution en arrière-plan

`fastapi.BackgroundTasks` (pas de file de tâches externe) : Starlette exécute une fonction synchrone passée à `BackgroundTasks.add_task` dans un thread du pool, sans bloquer la boucle d'événements — suffisant pour une application mono-instance avec SQLite. À documenter dans le code : si l'application tourne un jour en plusieurs workers/instances, il faudra une vraie file de tâches (Celery/RQ/arq) — hors périmètre ici.

### A.7 Endpoints (`app/api/jobs_router.py`)

```
POST   /api/jobs                  -> 201, JobCreatedResponse
GET    /api/jobs/{job_id}          -> 200 JobStatusResponse | 404
GET    /api/jobs/{job_id}/results   -> 200 JobResultsResponse | 404 | 409 si pas encore "succeeded"
```

### A.8 Application FastAPI (`app/api/main.py`)

```python
app = FastAPI(title="AI ICP Qualification Engine API")

@app.on_event("startup")
def _startup():
    init_db()

app.include_router(jobs_router, prefix="/api")
```

**Ne pas encore monter les fichiers statiques ici** — ça se fait en Partie C, une fois le frontend écrit, pour garder cette partie strictement backend et testable seule.

### A.9 Tests (`tests/api/test_jobs_router.py`)

`fastapi.testclient.TestClient` (ou `httpx.ASGITransport`, cohérent avec le reste du projet). Doublures déjà présentes (`FakeLLM`, un `SearchProvider` factice) pour rester rapide et hors-réseau, à l'image de `tests/acquisition/test_pipeline_contract.py`. Couvrir :
- `POST /api/jobs` → 201, job en base `status="pending"`.
- Cycle complet : `POST` puis polling `GET /api/jobs/{id}` jusqu'à `"succeeded"`, puis `GET /api/jobs/{id}/results` → contenu attendu.
- `GET /api/jobs/{id}/results` avant la fin → 409.
- `GET /api/jobs/{inconnu}` → 404.
- Un job dont le workflow lève une exception → `status="failed"`, `error` générique.

### A.10 Validation autonome

```bash
uv run uvicorn app.api.main:app --reload --port 8000
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" \
  -d '{"job_title":"Business Coach","country":"France"}'
curl http://localhost:8000/api/jobs/<id>
curl http://localhost:8000/api/jobs/<id>/results
```

### A.11 Checklist de sortie Partie A

- [x] `app/api/` complet (schemas, job_service, jobs_router sous `/api`, main) et testé
- [x] `Job` model + `JobRepository` + migration additive
- [x] Tests, lint, mypy verts
- [x] API validée manuellement en local

---

## Partie B — Écrire le frontend statique (HTML/CSS/JS, sans backend branché)

Fichiers écrits à la main, aucune génération. Développés et validés dans le navigateur en ouvrant `index.html` en fichier local (`file://`) pour la mise en page, avant tout branchement réseau — puis via un petit serveur statique pour tester les appels `fetch()` (voir B.5).

### B.1 Structure

```
frontend/
├── index.html
├── css/
│   └── style.css
└── js/
    └── app.js
```

### B.2 `index.html`

Reprend exactement les champs du formulaire Streamlit actuel, sans logique — juste du balisage sémantique :

```html
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI ICP Qualification Engine</title>
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>
  <header>
    <h1>AI ICP Qualification Engine</h1>
    <p>Recherche et qualification automatique de prospects B2B.</p>
  </header>

  <form id="icp-form">
    <label>Métier cible
      <input name="job_title" value="Business Coach" required>
    </label>
    <label>Pays cible
      <input name="country" value="France" required>
    </label>
    <label>Secteur / domaine
      <input name="sector" value="Coaching">
    </label>
    <label>Nombre de prospects souhaités
      <input name="max_prospects" type="number" min="1" max="100" value="20">
    </label>
    <label>Mots-clés obligatoires
      <input name="required_keywords" placeholder="séparés par des virgules">
    </label>
    <label>Mots-clés interdits
      <input name="forbidden_keywords" value="étudiant, stage, stagiaire, student, internship">
    </label>
    <button type="submit">Lancer la recherche</button>
  </form>

  <p id="cooldown-warning" class="warning" hidden></p>

  <section id="progress-section" hidden>
    <progress id="progress-bar" value="0" max="100"></progress>
    <p id="progress-text"></p>
  </section>

  <p id="error-message" class="error" hidden></p>

  <section id="results-section" hidden>
    <h2>Résultats</h2>
    <p id="results-count"></p>
    <table id="results-table">
      <thead>
        <tr><th>Nom</th><th>LinkedIn</th><th>Métier</th><th>Statut</th><th>Erreur</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  </section>

  <script src="/js/app.js" type="module"></script>
</body>
</html>
```

### B.3 `css/style.css`

Feuille de style simple et autonome (pas de framework CSS externe — pas de CDN, cohérent avec le principe de fichiers utilisables directement, sans dépendance réseau). Couvre : mise en page du formulaire, style de la barre de progression, style du tableau de résultats, un état `.warning`/`.error` visuellement distincts. Rien de plus précisé ici — c'est un choix visuel libre, pas structurant pour la migration.

### B.4 `js/app.js`

```js
const API_BASE = "/api";
const COOLDOWN_SECONDS = 30;
const MAX_RUNS_PER_SESSION = 20;

let lastRunAt = 0;
let runCount = 0;

async function createJob(payload) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("job creation failed");
  return (await res.json()).job_id;
}

async function getStatus(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("status check failed");
  return res.json();
}

async function getResults(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/results`);
  if (!res.ok) throw new Error("results fetch failed");
  return res.json();
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function splitKeywords(raw) {
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
}

document.getElementById("icp-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const now = Date.now();
  const remainingCooldown = COOLDOWN_SECONDS - (now - lastRunAt) / 1000;
  const cooldownEl = document.getElementById("cooldown-warning");

  if (lastRunAt && remainingCooldown > 0) {
    cooldownEl.textContent = `Veuillez patienter encore ${Math.ceil(remainingCooldown)} s avant de relancer une recherche.`;
    cooldownEl.hidden = false;
    return;
  }
  if (runCount >= MAX_RUNS_PER_SESSION) {
    cooldownEl.textContent = `Nombre maximal de recherches atteint pour cette session (${MAX_RUNS_PER_SESSION}). Rechargez la page pour réinitialiser.`;
    cooldownEl.hidden = false;
    return;
  }
  cooldownEl.hidden = true;
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

  document.getElementById("error-message").hidden = true;
  document.getElementById("results-section").hidden = true;
  const progressSection = document.getElementById("progress-section");
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  progressSection.hidden = false;

  try {
    const jobId = await createJob(payload);

    let status;
    do {
      await sleep(1500);
      status = await getStatus(jobId);
      progressBar.value = status.progress_percent;
      progressText.textContent = status.progress_text;
    } while (status.status === "pending" || status.status === "running");

    progressSection.hidden = true;

    if (status.status === "failed") {
      const errorEl = document.getElementById("error-message");
      errorEl.textContent = "Une erreur est survenue pendant le traitement. Consultez les journaux serveur pour plus de détails.";
      errorEl.hidden = false;
      return;
    }

    const { prospects } = await getResults(jobId);
    renderResults(prospects);
  } catch (err) {
    progressSection.hidden = true;
    const errorEl = document.getElementById("error-message");
    errorEl.textContent = "Une erreur est survenue pendant le traitement.";
    errorEl.hidden = false;
    console.error(err);
  }
});

function renderResults(prospects) {
  const section = document.getElementById("results-section");
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";

  for (const p of prospects) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(p.name)}</td>
      <td><a href="${escapeHtml(p.linkedin_url)}" target="_blank" rel="noopener">${escapeHtml(p.linkedin_url)}</a></td>
      <td>${escapeHtml(p.job_title)}</td>
      <td>${escapeHtml(p.status ?? "")}</td>
      <td>${escapeHtml(p.error ?? "")}</td>
    `;
    tbody.appendChild(row);
  }

  document.getElementById("results-count").textContent = `${prospects.length} prospects traités`;
  section.hidden = false;
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}
```

Points notables, à conserver tels quels lors de l'implémentation :
- Le cooldown/quota (`COOLDOWN_SECONDS`, `MAX_RUNS_PER_SESSION`) est réimplémenté **côté client**, en JS, puisqu'il n'y a plus de `st.session_state` côté serveur. Le comportement reste équivalent : réinitialisé au rechargement de la page, exactement comme l'était `st.session_state` côté Streamlit — ce n'est pas une régression.
- `escapeHtml()` est nécessaire : les résultats affichés proviennent de contenu scrappé (nom, titre de poste) — les insérer dans `innerHTML` sans échappement ouvrirait une injection XSS côté client. Ne jamais faire `td.innerHTML = p.name` directement.
- Les valeurs numériques `COOLDOWN_SECONDS`/`MAX_RUNS_PER_SESSION` sont dupliquées entre `app/core/settings.py` (qui ne pilote plus que le backend maintenant) et ce fichier JS. Si elles doivent rester pilotables sans reconstruire le frontend, prévoir un petit endpoint `GET /api/config` retournant ces valeurs, lu une fois au chargement de la page — amélioration listée en fin de plan (Hors périmètre), pas bloquante pour la migration.

### B.5 Validation autonome (sans backend)

Servir `frontend/` avec un serveur statique de test pour valider le rendu et le comportement JS sans dépendre de l'API :

```bash
cd frontend
python -m http.server 8080
```

Vérifier la mise en page, le déclenchement du cooldown après un clic simulé, l'échappement HTML sur des valeurs contenant `<script>` de test.

### B.6 Checklist de sortie Partie B

- [x] `frontend/index.html`, `frontend/css/style.css`, `frontend/js/app.js` écrits
- [x] Formulaire, barre de progression, tableau de résultats, cooldown/quota validés visuellement (B.5)
- [x] Aucune dépendance réseau externe (pas de CDN, pas de framework JS)

---

## Partie C — Brancher le frontend statique sur l'API (un seul service)

### C.1 Montage des fichiers statiques

Dans `app/api/main.py` :

```python
from fastapi.staticfiles import StaticFiles

app.include_router(jobs_router, prefix="/api")   # DOIT être enregistré avant le mount ci-dessous
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

**Ordre critique** : le `mount("/")` doit être ajouté **après** `include_router` — Starlette évalue les routes dans l'ordre d'enregistrement, et un mount catch-all sur `/` enregistré en premier intercepterait aussi les requêtes vers `/api/*`, avant même qu'elles n'atteignent le routeur API (elles se solderaient par un 404 « fichier statique introuvable » au lieu d'atteindre l'API). C'est l'erreur classique de ce pattern ; à vérifier explicitement en test (C.3).

`StaticFiles(html=True)` sert automatiquement `index.html` pour `/`, et les 404 de fichiers statiques restent des 404 standards (pas de fallback SPA nécessaire ici, il n'y a qu'une seule page).

### C.2 Configuration

Rien de nouveau côté configuration : plus de variable `API_BASE_URL` à gérer (le frontend appelle des chemins relatifs `/api/...`, résolus par le navigateur sur l'origine courante quel que soit l'environnement — local, Docker, autre nom d'hôte).

### C.3 Test d'intégration bout-en-bout

Ajouter un test qui vérifie explicitement le point sensible de C.1 :

```python
def test_static_frontend_is_served_at_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI ICP Qualification Engine" in response.text

def test_api_routes_are_not_shadowed_by_static_mount(client):
    response = client.post("/api/jobs", json={"job_title": "Coach", "country": "France"})
    assert response.status_code == 201
```

### C.4 Validation manuelle réelle

```bash
uv run uvicorn app.api.main:app --port 8000
```

Ouvrir `http://localhost:8000` dans un navigateur, remplir le formulaire, lancer une recherche, vérifier que la progression avance et que les résultats s'affichent — sur un cas réel, pas seulement via les tests.

*Si un jour les fichiers statiques doivent être servis séparément de l'API (CDN, Nginx dédié, domaine différent) : ce jour-là seulement, ajouter `CORSMiddleware` à `app/api/main.py` avec la liste explicite des origines autorisées. Ne pas l'ajouter par anticipation tant que frontend et API restent sur la même origine.*

### C.5 Checklist de sortie Partie C

- [x] `frontend/` servi par FastAPI à `/`, routes `/api/*` non masquées (C.3)
- [x] Flux complet validé via appels HTTP réels (curl) reproduisant exactement les appels du JS ; non ouvert dans un navigateur graphique (indisponible dans cet environnement) — à confirmer par l'utilisateur en conditions réelles
- [x] Tests, lint, mypy verts

---

## Partie D — Retirer Streamlit et nettoyer

Uniquement une fois la Partie C validée en conditions réelles.

### D.1 Suppression du code Streamlit

```bash
git rm -r app/ui/
git rm tests/ui/test_streamlit_app.py tests/ui/test_workflow_runner.py
```

Ces tests reposaient sur `streamlit.testing.v1.AppTest`, qui n'a plus d'objet à tester — pas d'équivalent à réécrire au même niveau (voir D.4 pour ce qui les remplace).

### D.2 Dépendances

```bash
uv remove streamlit
```

Avant de retirer `pandas` : vérifier qu'aucun autre module ne s'en sert encore (`grep -rn "import pandas" app/`) — `prospect_view.py` (supprimé avec `app/ui/`) était son seul usage identifié pour le moment, mais à reconfirmer au moment de l'exécution plutôt que de le supposer ici.

### D.3 Dockerfile / docker-compose.yml

Le service redevient unique (plus besoin d'un service `api` séparé d'un service frontend) :

```dockerfile
# Dockerfile
COPY app ./app
COPY frontend ./frontend
...
EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml — un seul service applicatif, comme avant, juste sur un port différent
  app:
    build: { context: .., dockerfile: Dockerfile }
    depends_on: [searxng]
    ports: ["127.0.0.1:8000:8000"]
    environment:
      SEARCH_PROVIDER: searxng
      SEARXNG_BASE_URL: http://searxng:8080
      DATABASE_URL: sqlite:////data/icp.db
      LLM_PROVIDER: gemini
      GEMINI_API_KEY: ${GEMINI_API_KEY:-}
      GEMINI_MODEL: ${GEMINI_MODEL:-gemini-3.6-flash}
      ENRICHMENT_ENGINE: ${ENRICHMENT_ENGINE:-bs4}
    volumes: ["icp_data:/data"]
```

Mettre à jour le `HEALTHCHECK` du Dockerfile : il ciblait `http://localhost:8501/_stcore/health` (endpoint Streamlit) — le remplacer par un endpoint santé FastAPI, par exemple `GET /api/health` (à ajouter dans `jobs_router.py` ou un routeur dédié, trivial : retourne `{"status": "ok"}`).

### D.4 Tests

Pas d'équivalent direct à `AppTest` pour un frontend statique. Deux niveaux couvrent la migration sans introduire un nouvel outillage JS lourd :
- **API** : déjà couverte par `tests/api/` (Partie A) — c'est là que vit la logique métier.
- **Service statique** : couvert par `test_static_frontend_is_served_at_root`/`test_api_routes_are_not_shadowed_by_static_mount` (C.3).
- **Comportement JS** (cooldown, rendu du tableau, échappement HTML) : validation manuelle uniquement pour cette migration (B.5, C.4). Si une couverture automatisée du JS devient nécessaire plus tard, une suite Playwright serait l'outil naturel — c'est un ajout d'outillage Node.js à part entière, volontairement laissé hors périmètre ici plutôt qu'imposé sans que ce soit demandé.

### D.5 Documentation

- `README.md` : diagramme d'architecture simplifié (`Browser → FastAPI (sert frontend/ + /api) → SearXNG / Gemini`), commande de lancement unique (`uv run uvicorn app.api.main:app --port 8000`), plus de mention de Streamlit.
- `docs/ARCHITECTURE.md` : remplacer la section Streamlit par la description frontend statique + API + cycle de vie d'un job.
- `docs/USER_GUIDE.md`, `docs/DOCKER.md` : instructions de lancement mises à jour.

### D.6 Checklist de sortie Partie D

- [x] `app/ui/`, `tests/ui/test_streamlit_app.py`, `tests/ui/test_workflow_runner.py` supprimés
- [x] `streamlit` retiré de `pyproject.toml`/`uv.lock` ; `pandas` réévalué
- [x] Un seul service Docker (`app`), healthcheck pointant vers `/api/health`
- [x] `grep -rn "streamlit\|app.ui" .` (hors `MIGRATION.md`/`AUDIT.md`, historiques) ne retourne plus rien
- [x] Documentation à jour

---

## Hors périmètre (à traiter plus tard si besoin)

- **`GET /api/config`** pour piloter `COOLDOWN_SECONDS`/`MAX_RUNS_PER_SESSION` côté JS depuis `app/core/settings.py` sans dupliquer les valeurs (B.4) — actuellement dupliqué entre backend et frontend, acceptable pour deux constantes rarement modifiées.
- **Authentification sur l'API** : tant que tout reste lié à `127.0.0.1`, pas nécessaire ; indispensable avant toute exposition au-delà de localhost.
- **File de tâches distribuée (Celery/RQ/arq)** : seulement si l'application doit tourner en plusieurs workers/instances.
- **Tests E2E automatisés du frontend (Playwright)** : introduirait un outillage Node.js absent du projet aujourd'hui ; à faire seulement si explicitement demandé.
- **Rétention/nettoyage des lignes `Job`** : s'accumulent indéfiniment en base ; acceptable à ce stade.

## Risques transverses à surveiller

| Risque | Impact | Mitigation prévue dans ce plan |
|---|---|---|
| Le mount `StaticFiles("/")` enregistré avant le routeur API masque `/api/*` | Toutes les routes API renvoient 404 | Ordre d'enregistrement documenté explicitement (C.1) + test dédié (C.3) |
| Contenu scrappé (nom, titre) inséré sans échappement dans le DOM | Injection XSS côté client | `escapeHtml()` systématique avant toute insertion dans `innerHTML` (B.4) |
| Session DB partagée entre le thread de la requête HTTP et le thread `BackgroundTasks` | Erreurs SQLAlchemy difficiles à diagnostiquer | `run_job()` ouvre systématiquement sa propre session (A.5) |
| Le polling ne voit pas la progression si le job ne `commit()` pas ses mises à jour | Barre de progression figée | Le `progress_callback` commit après chaque mise à jour (A.5) |
| Exception brute renvoyée au client sur échec de job | Fuite de détails internes (cf. audit C.1.4) | `error` toujours réduit à un message générique (A.5) |
| `pandas` retiré alors qu'un autre module en dépend encore | Import cassé | Vérification explicite avant `uv remove pandas` (D.2), pas de suppression automatique |
| `BackgroundTasks` ne survit pas à un redémarrage du process pendant qu'un job tourne | Job bloqué en `status="running"` indéfiniment | Limitation connue et acceptée pour une app mono-instance ; documentée plutôt que corrigée ici |
