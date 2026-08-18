# User Guide

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs and manages Python 3.13 for you)
- A Gemini API key for AI qualification
- Docker Desktop if SearXNG is used locally

## 1. Install

```powershell
uv sync
```

Create `.env` from `.env.example` and configure the LLM and database settings.

## 2. Start SearXNG

From the repository root:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Check the service:

```powershell
docker compose -f docker/docker-compose.yml ps
```

The local HTTP API is expected at:

```text
http://localhost:8080
```

A direct search check can be performed with PowerShell:

```powershell
Invoke-RestMethod "http://localhost:8080/search?q=site%3Alinkedin.com%2Fin%20%22Business%20Coach%22%20France&format=json"
```

If the connection is refused, inspect the container first:

```powershell
docker compose -f docker/docker-compose.yml logs --tail=100 searxng
```

## 3. Start the application

```powershell
uv run uvicorn app.api.main:app --port 8000
```

Open `http://localhost:8000` — FastAPI serves both the `/api/jobs*` endpoints and the static `frontend/` interface at `/`.

The interface lets you define the ICP dynamically:

- Métier cible
- Pays cible
- Secteur / domaine
- Mots-clés obligatoires
- Mots-clés interdits
- Nombre de prospects souhaités

Multiple keyword values are entered as comma-separated values.

After the workflow completes, the interface displays the number of prospects processed and the result table.

### Relaunch cooldown and session quota

To limit accidental repeated clicks from driving unnecessary Gemini/search cost, the "Lancer la recherche" button enforces a cooldown between runs and a maximum number of runs per browser session. This is enforced **client-side**, in `frontend/js/app.js` (reset whenever the page is reloaded), using the same default values also declared in `app/core/settings.py` for backend use:

- `WORKFLOW_COOLDOWN_SECONDS` (default `30`): minimum delay after a run before another one is accepted; a countdown warning is shown if you click again too soon.
- `MAX_WORKFLOW_RUNS_PER_SESSION` (default `20`): maximum number of workflow runs allowed within one page session; reload the page to reset the counter.

Changing these in `.env` affects the backend `Settings` values only — the frontend's own constants (`COOLDOWN_SECONDS`/`MAX_RUNS_PER_SESSION` in `frontend/js/app.js`) must be edited directly if you change the defaults, since the static frontend has no build step to inject configuration at deploy time (see `FASTAPI_MIGRATION.md`, "Hors périmètre", for the `GET /api/config` follow-up that would remove this duplication).

## 4. Reading the result table

Typical fields include:

- `Nom`: mapped prospect name.
- `LinkedIn`: normalized LinkedIn profile URL.
- `Métier`: extracted or enriched professional title.
- `Erreur`: execution error, when one occurred.

An error on one prospect does not necessarily mean that the acquisition/search stage failed for the complete workflow. Inspect the `Erreur` column when a candidate could not be fully processed.

## 5. Qualification and Gemini batching

Before the LLM stage, the engine applies deterministic exclusions, ICP pre-filtering and the ICP-scoped qualification cache.

Profiles that still require AI qualification are grouped into a batch. Gemini is then called once for the batch instead of once per profile. The returned qualification results are mapped back to the corresponding prospects.

This reduces unnecessary Gemini requests, especially when processing many prospects. Cached or deterministically filtered profiles are not sent to Gemini.

## 6. Search quality expectations

Search results are not accepted blindly. The acquisition layer performs relevance filtering and LinkedIn URL processing before enrichment.

SearXNG may aggregate engines with different behaviour. In particular, a `site:` operator should not be treated as universally reliable through every upstream engine. The query generator therefore provides a plain-text variant for unreliable operator handling.

Anti-bot responses such as CAPTCHA or access denied from individual upstream engines can reduce result quality without meaning that the application itself is broken.

## 7. Gemini quota errors

The qualification stage uses Gemini. Free-tier quotas can cause errors such as:

```text
429 RESOURCE_EXHAUSTED
```

This means the API quota or rate limit was exhausted. It is distinct from a prospect being rejected by the ICP.

Because qualification is batched, one API request can cover several profiles. The exact number of Gemini requests depends on the number of profiles that survive pre-filtering and cache lookup, the batch implementation and any retries or failures.

## 8. API / SQLAlchemy session handling

The application uses SQLAlchemy sessions with `expire_on_commit=False`. This keeps ORM attributes available after commits when workflow results are consumed and serialized by `app/api/job_service.py`.

The workflow/database boundary remains responsible for session ownership. `run_job()` (the background task that executes a job) always opens its own session via `SessionLocal()` — never the session used to handle the HTTP request that created the job, since that request's session is already closed by the time the background task runs.

If an error such as the following appears:

```text
Instance <Prospect ...> is not bound to a Session; attribute refresh operation cannot proceed
```

verify that the current repository version is installed and that the workflow has not been modified to close its session before result consumption.

## 9. Development test suite

Run only non-integration tests, as CI does (recommended default):

```powershell
uv run pytest -q -m "not integration"
```

Run all tests, including the Gemini integration tests:

```powershell
uv run pytest -q
```

**Warning:** the full suite hits the real Gemini API and consumes real quota/cost if `GEMINI_API_KEY` is set in `.env`. Prefer the non-integration command above for routine development.

The integration marker is defined in the pytest configuration and external-service tests should be treated separately from deterministic unit tests.
