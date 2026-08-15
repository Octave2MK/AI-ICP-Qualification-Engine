# AI ICP Qualification Engine

> **ICP-driven B2B prospect sourcing, OSINT enrichment and AI qualification engine.**

AI ICP Qualification Engine discovers public B2B prospects, filters them against a dynamic Ideal Customer Profile (ICP), enriches their public profile data and produces a structured qualification, decision and score.

The project is designed for:

- B2B prospecting and lead generation
- sales intelligence
- outbound research
- coach, consultant and expert discovery
- ICP-based market research

## Why this project?

The objective is not simply to collect profiles. The engine progressively reduces noise before spending enrichment and LLM resources:

```text
Dynamic ICP
    ↓
Query generation
    ↓
Search discovery
    ↓
Relevance filtering
    ↓
LinkedIn URL extraction + normalization
    ↓
Deduplication
    ↓
Prospect mapping
    ↓
OSINT enrichment
    ↓
ICP pre-filter + exclusions
    ↓
ICP-scoped AI qualification
    ↓
Decision + confidence threshold
    ↓
Hybrid scoring
    ↓
Persistence
    ↓
Streamlit results
```

The differentiator is the combination of **ICP-first discovery, search-based OSINT, deterministic filtering and LLM reasoning**, rather than relying exclusively on a static lead database.

## Core capabilities

### Dynamic ICP

The Streamlit interface builds the ICP at runtime. Current acquisition criteria include:

- target job titles
- countries
- languages
- sectors
- keywords
- required keywords
- forbidden keywords

Qualification uses a dynamic `ICPDefinition` containing professions, sectors, target markets, required/forbidden keywords and `minimum_confidence`.

The pipeline does not hard-code a `business_coach` ICP.

### Search abstraction

Search infrastructure is behind a provider interface:

```text
SearchProvider
├── DuckDuckGoProvider
└── SearXNGProvider
```

SearXNG is an external local metasearch service. The application talks to it over HTTP. Because upstream engines do not necessarily handle search operators consistently, `QueryGenerator` also produces a plain-text query variant that does not depend on `site:`.

### Relevance and acquisition pipeline

```text
SearchResult
 ↓
RelevanceFilter
 ↓
URLExtractor
 ↓
URLNormalizer
 ↓
Deduplicator
 ↓
ProspectMapper
```

The `ProspectMapper` extracts a clean name and professional title from LinkedIn result titles while preserving legitimate internal hyphens and removing the final LinkedIn suffix.

### Qualification

Qualification is deliberately hybrid:

```text
Deterministic exclusions
        ↓
ICP pre-filter
        ↓
ICP-specific cache lookup
        ↓
Gemini batch qualification
        ↓
Validation
        ↓
Decision / minimum_confidence
        ↓
Hybrid score
```

When several profiles require AI qualification during one workflow, the service uses Gemini batch analysis so eligible profiles can be qualified in a single LLM request rather than making one request per profile. Profiles rejected before qualification or already present in the ICP-scoped cache are not sent to Gemini.

The qualification cache is scoped by **prospect + ICP fingerprint**, allowing the same prospect to be evaluated independently against different ICPs.

### Streamlit interface

The Streamlit interface lets the user define an ICP and launch the complete workflow. After processing, it displays the number of prospects processed and a result table containing the available prospect, qualification and error information.

## Architecture

The codebase is organized around separated application concerns:

```text
app/
├── acquisition/     # search, filtering, URL processing and acquisition
├── batch/           # batch processing
├── cache/           # application caching
├── core/            # settings and logging
├── database/        # SQLAlchemy models/database
├── enrichment/      # OSINT profile enrichment
├── exceptions/      # application exceptions
├── pipeline/        # end-to-end orchestration
├── qualification/   # ICP, LLM qualification and decisions
├── repositories/    # persistence access
├── scoring/         # hybrid scoring
├── ui/              # Streamlit interface
└── factory.py       # application factories
```

The project follows Clean Architecture-inspired separation, dependency injection, interface-based infrastructure and single-responsibility components.

For a detailed technical description, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

For installation and operational instructions, see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

For development conventions and safe-change workflow, see [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Installation

Requirements:

- Python 3.13
- Docker Desktop for local SearXNG
- Gemini API key for AI qualification

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Create `.env`:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables, including the Gemini API key and application database settings.

**Never commit `.env` or API keys.**

## Run SearXNG locally

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Check it:

```powershell
docker compose -f docker/docker-compose.yml ps
```

The host binding is intentionally local-only:

```text
127.0.0.1:8080:8080
```

Test the HTTP API:

```powershell
Invoke-RestMethod "http://localhost:8080/search?q=site%3Alinkedin.com%2Fin%20%22Business%20Coach%22%20France&format=json"
```

If the connection is refused, inspect the container:

```powershell
docker compose -f docker/docker-compose.yml logs --tail=100 searxng
```

## Run the application

```powershell
streamlit run app/ui/streamlit_app.py
```

Then define the ICP in the interface and launch the workflow.

## Testing

Run the full suite:

```powershell
pytest -q
```

Run the CI-equivalent non-integration suite:

```powershell
pytest -q -m "not integration"
```

Integration tests are marked in `pytest.ini` and are intentionally excluded from the default GitHub Actions test command because they can require external services, credentials or quotas.

GitHub Actions is configured in `.github/workflows/tests.yml` for pushes and pull requests targeting `main`.

## Gemini quota errors

The AI qualification stage uses Gemini. Free-tier or project limits can produce:

```text
429 RESOURCE_EXHAUSTED
```

This is an infrastructure/API limitation. It should be treated as an execution error rather than a prospect rejection.

## SearXNG and search quality

SearXNG can aggregate several upstream search engines. Their availability and interpretation of operators can vary. CAPTCHA, access-denied responses and inconsistent `site:` handling can therefore affect individual searches.

The application mitigates operator reliability by generating a plain-text query variant in addition to operator-based variants. This does not guarantee that every upstream engine returns LinkedIn-only results; downstream relevance filtering and URL validation remain essential.

## Security notes

- `.env` and credentials must remain outside version control.
- The local SearXNG host port is bound to `127.0.0.1`.
- `docker/settings.yml` contains a generated local secret key and is intended for local development.
- Before any Internet-facing deployment, review SearXNG authentication, secret management, bind addresses, rate limiting and reverse-proxy configuration.

## Current status

| Area | Status |
|---|---|
| Dynamic ICP | ✅ |
| Query generation | ✅ |
| Search provider abstraction | ✅ |
| DuckDuckGo provider | ✅ |
| SearXNG provider | ✅ |
| Relevance filtering | ✅ |
| LinkedIn URL extraction/normalization | ✅ |
| Prospect mapping | ✅ |
| OSINT enrichment | ✅ |
| ICP pre-filter | ✅ |
| ICP-scoped qualification cache | ✅ |
| Gemini batch qualification | ✅ |
| Minimum confidence | ✅ |
| Hybrid scoring | ✅ |
| SQLite persistence | ✅ |
| Streamlit workflow | ✅ |
| Automated tests | ✅ |
| GitHub Actions CI | ✅ |
| Production hardening | 🚧 |

## Roadmap

The next engineering priorities are production hardening and empirical validation rather than adding more architectural layers prematurely:

- real multi-search evaluation and ground-truth datasets
- precision/recall measurement and threshold calibration
- robust search-provider fallback strategy
- improved enrichment coverage
- PostgreSQL production support
- API layer
- multi-LLM support
- observability and monitoring
- authentication and multi-tenant workspaces

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — technical architecture and component contracts
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — installation, SearXNG, Streamlit and troubleshooting
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — development workflow, invariants and testing rules

## License

No open-source license has been declared in the repository yet. Unless a license is added, normal copyright restrictions apply.
