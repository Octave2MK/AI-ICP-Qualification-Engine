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
 ├─ LLM qualification
 ├─ validation
 ├─ decision
 └─ hybrid scoring
 ↓
Persistence / reporting / Streamlit
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

## 5. Qualification

`ICPQualificationPipeline.run()` applies the following order:

1. Exclusion rules.
2. Deterministic ICP pre-filter.
3. Lookup in the qualification cache using prospect ID + ICP fingerprint.
4. LLM qualification when no cache entry exists.
5. Persistence of the qualification with the current ICP fingerprint.
6. Decision using the ICP's `minimum_confidence`.
7. Hybrid scoring.

This separation keeps deterministic safeguards around the LLM rather than allowing the model to control the entire workflow.

## 6. Streamlit

`app/ui/streamlit_app.py` builds the dynamic ICP from user input and calls the workflow runner. Results are converted to a dataframe for display.

The UI also reports three distinct workflow outcomes:

```text
X réussis / Y erreurs / Z filtrés
```

A successful item means the workflow reached a normal qualification result without an execution error. An item with a Gemini/API failure is an error, not a successful qualification. A deterministic rejection before/without successful qualification is represented as filtered according to the reporting layer.

## 7. Persistence

The current local persistence stack is SQLAlchemy + SQLite. Qualification records are scoped to the ICP fingerprint to prevent cross-ICP cache contamination.

## 8. Infrastructure

SearXNG is provided through Docker Compose. The current compose configuration binds the host port to `127.0.0.1:8080`, keeping the local SearXNG API inaccessible from other network interfaces by default.

The SearXNG container itself listens internally on its container interface; the host exposure is what is restricted.

## 9. Testing and CI

The repository has an automated pytest suite and a GitHub Actions workflow at `.github/workflows/tests.yml`. CI runs Python 3.13, installs runtime and development dependencies, and executes the non-integration test suite.

Integration tests requiring external services are intentionally excluded from the default CI command.
