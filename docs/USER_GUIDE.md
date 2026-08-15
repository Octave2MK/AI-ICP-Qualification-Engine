# User Guide

## Prerequisites

- Python 3.13
- A Gemini API key for AI qualification
- Docker Desktop if SearXNG is used locally

## 1. Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
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

A direct health/search check can be performed with PowerShell:

```powershell
Invoke-RestMethod "http://localhost:8080/search?q=site%3Alinkedin.com%2Fin%20%22Business%20Coach%22%20France&format=json"
```

If the connection is refused, inspect the container first:

```powershell
docker compose -f docker/docker-compose.yml logs --tail=100 searxng
```

## 3. Start Streamlit

```powershell
streamlit run app/ui/streamlit_app.py
```

The interface lets you define the ICP dynamically:

- Métier cible
- Pays cible
- Secteur / domaine
- Mots-clés obligatoires
- Mots-clés interdits
- Nombre de prospects souhaités

Multiple keyword values are entered as comma-separated values.

After the workflow completes, the interface keeps the presentation intentionally simple: it displays the number of prospects processed and the result table. There is no separate reporting dashboard or success/error/filtered summary layer.

## 4. Reading the result table

Typical fields include:

- `Nom`: mapped prospect name.
- `LinkedIn`: normalized LinkedIn profile URL.
- `Métier`: extracted or enriched professional title.
- `Score ICP`: resulting qualification/scoring value.
- `ICP Match`: whether the qualification matches the current ICP.
- `Confiance`: model confidence used by the decision layer.
- `Offre B2B`: detected B2B offer signal.
- `Secteur`: qualified sector.
- `Profession`: qualified profession.
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

This means the API quota/rate limit was exhausted. It is distinct from a prospect being rejected by the ICP.

Because qualification is batched, one API request can cover several profiles. The exact number of Gemini requests depends on the number of profiles that survive pre-filtering and cache lookup, the batch implementation and any retries/failures.

## 8. Streamlit / SQLAlchemy session errors

The Streamlit workflow keeps the database session alive while the end-to-end workflow executes and configures SQLAlchemy sessions with `expire_on_commit=False`.

This prevents ORM objects returned by the workflow from being expired immediately after a commit and then failing when the UI accesses their attributes after the session lifecycle changes.

If you see an error such as:

```text
Instance <Prospect ...> is not bound to a Session; attribute refresh operation cannot proceed
```

first make sure the local repository contains the current `SessionLocal` configuration and that the workflow does not close the session before all required ORM attributes have been materialized. Do not work around the error by opening random extra sessions in the Streamlit layer; session ownership belongs to the workflow runner/database boundary.

## 9. Development test suite

Run all tests:

```powershell
pytest -q
```

Run only non-integration tests, as CI does:

```powershell
pytest -q -m "not integration"
```

The integration marker is defined in the pytest configuration and external-service tests should be treated separately from deterministic unit tests.
