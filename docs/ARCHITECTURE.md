# Architecture

## 1. Overview

AI ICP Qualification Engine is a modular B2B prospecting and qualification system. It starts from a dynamic `ICP`, discovers public candidates through search infrastructure, filters them deterministically, enriches public profile data, qualifies the profile with an LLM, applies deterministic decisions and stores the result.

The main flow is:

```text
ICP
 ↓
QueryGenerator
 ↓
SearchProvider
 ↓
SearchResult
 ↓
RelevanceFilter
 ↓
URLExtractor / URLNormalizer
 ↓
Deduplicator
 ↓
ProspectMapper
 ↓
OSINT enrichment
 ↓
ICPQualificationPipeline
 ├─ exclusion
 ├─ ICP pre-filter
 ├─ ICP-scoped qualification cache
 ├─ LLM batch qualification
 ├─ validation
 ├─ decision
 └─ hybrid scoring
 ↓
Persistence
 ↓
API job result / web UI
```

## 2. Dynamic ICP

The acquisition model contains `job_titles`, `countries`, `languages`, `sectors`, `keywords`, `required_keywords` and `forbidden_keywords`.

Qualification uses `ICPDefinition`, which contains professions, sectors, target markets, required/forbidden keywords and `minimum_confidence`.

The qualification pipeline receives the ICP at runtime. It does not depend on a hard-coded `business_coach` ICP.

`ICPDefinition.fingerprint()` produces a stable SHA-256 identifier from the complete ICP definition. The fingerprint is used by qualification persistence so the same prospect can be evaluated independently against multiple ICPs.

## 3. Acquisition

`SearchProvider` is the abstraction used by the acquisition layer. Current implementations are DuckDuckGo and SearXNG.

`QueryGenerator` generates ICP-driven queries. It also supports a plain-text query variant that does not depend on the `site:` operator. This is intentional: metasearch adapters and upstream engines do not always preserve search operators reliably.

SearXNG is an external local service. The application communicates with it over HTTP. SearXNG can aggregate multiple upstream engines, but the application should not assume that every upstream engine handles operators or anti-bot conditions identically.

## 4. Candidate filtering

`RelevanceFilter` operates on search-result title/snippet signals before enrichment. This is a cost-control boundary: irrelevant candidates should not consume enrichment or LLM resources.

The acquisition chain then validates and normalizes LinkedIn URLs, removes duplicates and maps a `ProspectCandidate` to a database `Prospect`.

`ProspectMapper` extracts a clean display name and job title from common LinkedIn result-title patterns such as:

```text
Pascal BENVENISTE - Business Coach. Accompagnement des dirigeants - LinkedIn
```

The final `- LinkedIn` suffix is removed while legitimate internal hyphens remain part of the job title.

## 5. OSINT enrichment

`EnrichmentFactory` selects the enrichment engine via `settings.ENRICHMENT_ENGINE`:

- `"bs4"` (default): `EnrichmentService` fetches and parses one LinkedIn profile at a time, via `PageFetcher` (requests) and `ProfileExtractor` (BeautifulSoup). `PageFetcher` validates the resolved host against private/loopback/link-local/reserved IP ranges before each request (including after a redirect) and caps response size, to guard against SSRF.
- `"scrapy"`: `ScrapyBatchEnricher` crawls every acquired LinkedIn URL in one Scrapy run per workflow execution, launched in a dedicated subprocess (`app/enrichment/scrapy_crawler/`). Scrapy's Twisted reactor can only start once per OS process, which is incompatible with the long-lived FastAPI/uvicorn process serving the API — hence the subprocess isolation. The crawler applies the same SSRF-style host restriction (`SafeHostDownloaderMiddleware`) and reproduces `ProfileExtractor`'s extraction logic exactly (title as headline, full document text as raw text), so switching engines is behavior-neutral for the qualification stage downstream.

Both engines produce the same `ProfileData` shape and are consumed identically by `FullICPWorkflow`, which dispatches to a per-prospect loop (`"bs4"`) or a single batch call (`"scrapy"`) based on `isinstance(enricher, BaseBatchEnricher)`. A prospect whose URL fails enrichment — individually in the `"bs4"` loop, or is simply absent from the `"scrapy"` batch result — is recorded as an error entry rather than aborting the whole workflow.

## 6. Qualification

`ICPQualificationPipeline.run()` applies the following order:

1. Exclusion rules.
2. Deterministic ICP pre-filter.
3. Lookup in the qualification cache using prospect ID + ICP fingerprint.
4. LLM qualification when no cache entry exists.
5. Persistence of the qualification with the current ICP fingerprint.
6. Decision using the ICP's `minimum_confidence`.
7. Hybrid scoring.

For the production workflow, `run_batch()` applies the same preparation and cache checks to all pending profiles and sends the remaining profiles to `QualificationService.qualify_batch()`. The LLM receives one batch request for the pending profiles rather than one request per profile.

## 7. API and web interface

`app/api/main.py` is the FastAPI application. It includes `jobs_router` (prefixed `/api`) and mounts `frontend/` as static files at `/` — the API router must be included before the static mount, otherwise the catch-all static handler would shadow `/api/*`.

The workflow runs as an asynchronous job rather than inline in the HTTP request, because a full run (search + enrichment + qualification) can take several minutes:

```text
POST /api/jobs
 ↓ creates a Job row (status="pending"), schedules run_job() as a
   fastapi.BackgroundTasks task, returns job_id immediately
 ↓
run_job() (background thread)
 ↓ opens its own DB session (never the request's session)
 ↓ status="running", builds ICP, calls create_full_workflow(db).run(...)
 ↓ progress_callback commits progress_percent/progress_text after each step
 ↓
status="succeeded" (results serialized to JSON on the Job row)
  or status="failed" (generic error message; full exception logged server-side only)
```

`GET /api/jobs/{id}` and `GET /api/jobs/{id}/results` read the `Job` row (`app/database/models.py`) via `JobRepository`. A single-instance app with `BackgroundTasks` is sufficient here; a distributed task queue would only be needed if the API ran across multiple worker processes/instances.

`frontend/index.html` + `frontend/js/app.js` build the ICP form, `fetch()` the endpoints above, poll job status, and render the result table — plain JavaScript, no framework, no build step. Because the frontend is served from the same origin as the API, no CORS configuration is required in the default deployment.

## 8. Persistence

The current local persistence stack is SQLAlchemy + SQLite. Qualification records are scoped to the ICP fingerprint to prevent cross-ICP cache contamination.

SQLAlchemy sessions use `expire_on_commit=False` so ORM objects returned by the workflow remain readable after commits when they are consumed by the result-serialization layer. Session ownership remains at the workflow/database boundary; `run_job()`'s background-task session is always distinct from the session used to handle the originating HTTP request.

## 9. Infrastructure

SearXNG is provided through Docker Compose. The current compose configuration binds the host port to `127.0.0.1:8080`, keeping the local SearXNG API inaccessible from other network interfaces by default.

The SearXNG container itself listens internally on its container interface; the host exposure is what is restricted.

## 10. Testing and CI

The repository has an automated pytest suite and a GitHub Actions workflow at `.github/workflows/tests.yml`. CI runs Python 3.13, installs runtime and development dependencies, and executes the non-integration test suite.

Integration tests requiring external services are intentionally excluded from the default CI command.
