# AI ICP Qualification Engine

> **ICP-driven B2B prospect sourcing, OSINT enrichment and AI qualification engine.**

AI ICP Qualification Engine discovers public B2B prospects, filters them against a dynamic Ideal Customer Profile (ICP), enriches their public profile data and produces a structured qualification, decision and score.

The project is designed for:

- B2B prospecting and lead generation
- sales intelligence
- outbound research
- coach, consultant and expert discovery
- ICP-based market research

## Quick start for users

The easiest way to run the complete application is **Docker**. You do not need to install Python or the project dependencies on your computer.

### Prerequisites

- Docker Desktop with Docker Compose
- A Gemini API key for AI qualification
- Git, if cloning the repository from GitHub

### 1. Clone the repository

```powershell
git clone https://github.com/Octave2MK/AI-ICP-Qualification-Engine.git
cd AI-ICP-Qualification-Engine
```

### 2. Create the local configuration

Create the SearXNG configuration from the committed template:

```powershell
Copy-Item docker/settings.yml.example docker/settings.yml
```

Open `docker/settings.yml` and replace `CHANGE_ME_TO_A_RANDOM_SECRET` with a random secret value. This local file is ignored by Git.

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` or share your API key.

### 3. Start the application

```powershell
docker compose -f docker/docker-compose.yml up -d --build
```

Then open:

**http://localhost:8501**

Define your ICP in Streamlit and launch the workflow.

### Useful Docker commands

Check the services:

```powershell
docker compose -f docker/docker-compose.yml ps
```

View application logs:

```powershell
docker compose -f docker/docker-compose.yml logs -f app
```

View SearXNG logs:

```powershell
docker compose -f docker/docker-compose.yml logs -f searxng
```

Stop the application without deleting the database:

```powershell
docker compose -f docker/docker-compose.yml down
```

Start it again without rebuilding:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

The SQLite database is stored in the Docker-managed `icp_data` volume and therefore survives a normal `docker compose down`.

To intentionally delete the persisted database:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

### What Docker runs

```text
Browser
   ↓
Streamlit :8501
   ↓ HTTP
SearXNG :8080
   ↓
Upstream search engines
```

The application communicates with SearXNG through the Docker network at `http://searxng:8080`. The host-facing SearXNG port is only available locally at `127.0.0.1:8080`.

The Gemini API key is passed to the application container through the environment; it is not baked into the Docker image.

For the complete Docker reference, see [`docs/DOCKER.md`](docs/DOCKER.md).

## Developer setup

Python is required only when developing or testing the application outside Docker. Dependencies are managed with [uv](https://docs.astral.sh/uv/).

Requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs and manages Python 3.13 for you)
- Docker Desktop for local SearXNG when running the application directly from Python
- Gemini API key for AI qualification

Install dependencies and create the virtual environment:

```powershell
uv sync
```

This creates `.venv` and installs both runtime and development dependencies from `uv.lock`.

Create `.env`:

```powershell
Copy-Item .env.example .env
```

When running the application directly with Python, configure the local SearXNG URL and database settings in `.env` as appropriate for your environment. Do not commit `.env` or API keys.

Run the application:

```powershell
uv run streamlit run app/ui/streamlit_app.py
```

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

### OSINT enrichment engines

Enrichment is behind an `ENRICHMENT_ENGINE` setting:

```text
EnrichmentFactory
├── "bs4"    (default) — requests + BeautifulSoup, one profile fetched at a time
└── "scrapy" — a batch Scrapy crawl per workflow run, in a dedicated subprocess
```

The `scrapy` engine crawls every acquired LinkedIn URL in a single run instead of fetching profiles one by one, mirroring the batch approach already used for Gemini qualification. It runs Scrapy in a separate subprocess rather than in-process, because Scrapy's Twisted reactor can only start once per process — incompatible with the long-lived Streamlit process. See [`MIGRATION.md`](MIGRATION.md), partie B, for the full design rationale.

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

For Docker usage, see [`docs/DOCKER.md`](docs/DOCKER.md).

For development conventions and safe-change workflow, see [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Testing

Run the CI-equivalent non-integration suite (recommended default for day-to-day development):

```powershell
uv run pytest -q -m "not integration"
```

Run the full suite, including integration tests:

```powershell
uv run pytest -q
```

**Warning:** the full suite hits the real Gemini API (`tests/integration/`) and consumes real quota/cost if `GEMINI_API_KEY` is set in `.env`. Prefer the non-integration command above unless you specifically intend to exercise the Gemini integration tests.

Integration tests are marked via the `integration` marker declared in `pyproject.toml` (`[tool.pytest.ini_options]`) and are intentionally excluded from the default GitHub Actions test command because they can require external services, credentials or quotas.

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
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — installation, Streamlit and troubleshooting
- [`docs/DOCKER.md`](docs/DOCKER.md) — Docker deployment and end-user setup
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — development workflow, invariants and testing rules

## License

No open-source license has been declared in the repository yet. Unless a license is added, normal copyright restrictions apply.
