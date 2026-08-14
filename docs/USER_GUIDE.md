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

Multiple keyword values are entered as comma-separated values.

## 4. Understand the workflow result

The interface reports:

```text
X réussis / Y erreurs / Z filtrés
```

- **Réussis**: the workflow completed normally and produced a qualification result.
- **Erreurs**: processing failed for the candidate, for example because the Gemini API returned a quota/rate-limit error.
- **Filtrés**: the candidate was rejected by deterministic filtering/exclusion logic and therefore did not require a normal LLM qualification result.

A Gemini `429 RESOURCE_EXHAUSTED` is an infrastructure/API error. It must not be interpreted as an ICP rejection.

## 5. Reading the result table

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

## 6. Search quality expectations

Search results are not accepted blindly. The acquisition layer performs relevance filtering and LinkedIn URL processing before enrichment.

SearXNG may aggregate engines with different behaviour. In particular, a `site:` operator should not be treated as universally reliable through every upstream engine. The query generator therefore provides a plain-text variant for unreliable operator handling.

Anti-bot responses such as CAPTCHA or access denied from individual upstream engines can reduce result quality without meaning that the application itself is broken.

## 7. Gemini quota errors

The qualification stage uses Gemini. Free-tier quotas can cause errors such as:

```text
429 RESOURCE_EXHAUSTED
```

This means the API quota/rate limit was exhausted. It is distinct from a prospect being filtered by the ICP.

When testing the complete workflow, monitor the error count separately from the filtered count.

## 8. Development test suite

Run all tests:

```powershell
pytest -q
```

Run only non-integration tests, as CI does:

```powershell
pytest -q -m "not integration"
```

The integration marker is defined in the pytest configuration and external-service tests should be treated separately from deterministic unit tests.
