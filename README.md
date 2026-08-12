# AI ICP Qualification Engine

> **AI-powered B2B prospect sourcing, enrichment and qualification engine built around ICP-driven OSINT, modular search providers and LLM-based qualification.**

AI ICP Qualification Engine is a modular OSINT engine designed to discover, filter, enrich and qualify B2B prospects against an **Ideal Customer Profile (ICP)**.

The project is designed for use cases such as:

* B2B lead generation
* prospect sourcing
* sales intelligence
* outbound prospecting
* consultant and coach acquisition
* expert and freelancer discovery
* ICP-based market research

The engine combines deterministic rules, search-engine data, OSINT enrichment and LLM-based qualification into a modular pipeline.

---

## 🎯 Core objective

Traditional prospecting tools often rely heavily on predefined databases, static filters or expensive proprietary data sources.

This project takes a different approach:

```text
ICP
 ↓
Query generation
 ↓
Search engine discovery
 ↓
Relevance filtering
 ↓
LinkedIn URL extraction
 ↓
URL normalization
 ↓
Deduplication
 ↓
OSINT enrichment
 ↓
AI qualification
 ↓
Decision engine
 ↓
Hybrid scoring
 ↓
Persistence
```

The objective is not simply to **find profiles**.

The objective is to identify profiles that are **actually relevant to a specific ICP**.

---

# ✨ Key features

## 🔎 ICP-driven acquisition

The acquisition engine generates search queries from an ICP rather than relying on manually written queries.

An ICP can contain criteria such as:

* target job titles
* countries
* languages
* keywords
* required keywords
* forbidden keywords

Example:

```text
Job title: Business Coach
Country: France
Keywords: coaching, entrepreneur
Forbidden keywords:
student
étudiant
intern
internship
stagiaire
job seeker
```

---

## 🌐 Modular search architecture

Search engines are abstracted behind the `SearchProvider` interface.

```text
SearchProvider
      │
      ├── DuckDuckGoProvider
      │
      └── SearXNGProvider
```

A `ProviderFactory` selects the configured provider.

This makes the acquisition layer independent from a specific search engine and allows additional providers to be introduced without rewriting the pipeline.

### Current providers

* DuckDuckGo
* SearXNG

SearXNG acts as a search aggregation layer and can expose results from multiple underlying search engines.

The application communicates with SearXNG through HTTP rather than embedding the search engine directly into the domain logic.

---

# 🧠 Relevance filtering

Search results are filtered **before expensive enrichment operations**.

The relevance engine evaluates:

* professional title
* search-result snippet
* ICP keywords
* country
* forbidden keywords

Example scoring model:

| Signal                              | Score |
| ----------------------------------- | ----: |
| Exact professional title in title   |   +50 |
| Professional title in search result |   +40 |
| ICP keyword in title                |   +15 |
| ICP keyword in snippet              |   +10 |
| Country detected                    |   +10 |
| Forbidden keyword                   |  -100 |

Default relevance threshold:

```text
50
```

This pre-filter prevents obviously irrelevant profiles from entering the enrichment and AI qualification stages.

For example:

```text
Business Coach detected in snippet    +40
France detected                       +10
-------------------------------------------
Total                                  50
```

The candidate therefore passes the acquisition relevance threshold.

---

# 🔗 LinkedIn URL processing

The acquisition pipeline processes discovered URLs through several deterministic stages:

```text
SearchResult
    ↓
URLExtractor
    ↓
URLNormalizer
    ↓
Deduplicator
```

This provides:

* LinkedIn profile URL extraction
* URL normalization
* duplicate removal
* deterministic processing before enrichment

---

# ⚡ Acquisition pipeline

The central acquisition pipeline is composed of explicit dependencies:

```text
QueryGenerator
SearchProvider
RelevanceFilter
URLExtractor
URLNormalizer
Deduplicator
ProspectMapper
```

Conceptually:

```python
pipeline = AcquisitionPipeline(
    query_generator=...,
    search_provider=...,
    relevance_filter=...,
    url_extractor=...,
    normalizer=...,
    deduplicator=...,
    prospect_mapper=...,
)
```

The pipeline is therefore independently testable and does not depend on a concrete search engine.

---

# 🛡️ Resilience mechanisms

The search layer includes infrastructure designed for real-world acquisition workloads.

Current components include:

* retry handling
* rate limiting
* search caching
* provider abstraction
* search error handling
* logging
* provider factory
* SearXNG-specific caching and logging

A failed search query does not necessarily terminate the complete acquisition process.

The pipeline is designed to continue processing remaining queries when a provider error occurs.

---

# 🧩 OSINT enrichment

Once relevant profiles have been discovered, the project can continue with OSINT enrichment.

The enrichment layer is responsible for transforming publicly available information into structured profile data.

The architecture separates acquisition from enrichment so that:

```text
Search discovery
```

and

```text
Profile enrichment
```

remain independent concerns.

This makes it possible to change the search infrastructure without rewriting the enrichment system.

---

# 🤖 AI qualification

After acquisition and enrichment, the project uses an LLM-based qualification layer.

The current architecture supports:

* LLM abstraction
* Gemini integration
* fake/mock LLM implementations for tests
* prompt construction
* structured JSON parsing
* result validation
* semantic normalization
* exclusion logic
* decision logic

The LLM is therefore not responsible for the entire application logic.

Instead:

```text
Deterministic acquisition
        ↓
OSINT enrichment
        ↓
LLM qualification
        ↓
Deterministic validation
        ↓
Decision
```

This hybrid approach reduces the risk of allowing an LLM to make uncontrolled decisions.

---

# 📊 Hybrid scoring

The project combines deterministic signals and AI qualification.

The scoring architecture can incorporate:

* ICP relevance
* professional signals
* qualification results
* exclusion signals
* semantic matching
* decision-engine outputs

The goal is to produce a structured prospect score rather than a simple binary:

```text
relevant / irrelevant
```

---

# 💾 Persistence

The application uses SQLAlchemy with SQLite for local persistence.

The database layer is separated from acquisition and qualification logic.

This allows the application to:

* persist prospects
* retrieve prospects
* maintain qualification information
* support caching
* separate persistence concerns from domain logic

PostgreSQL is planned as a future production-oriented database option.

---

# 🏗️ Architecture

The project follows a modular architecture inspired by **Clean Architecture**, with explicit separation of responsibilities.

High-level structure:

```text
Presentation
     ↓
Application
     ↓
Domain
     ↓
Infrastructure
```

Current application modules include:

```text
app/
├── acquisition/
├── batch/
├── cache/
├── core/
├── database/
├── enrichment/
├── exceptions/
├── pipeline/
├── qualification/
├── reporting/
├── repositories/
├── scoring/
├── ui/
├── factory.py
└── main.py
```

The acquisition module currently contains:

```text
app/acquisition/
├── acquisition_models.py
├── deduplicator.py
├── duckduckgo_provider.py
├── exceptions.py
├── normalizer.py
├── pipeline.py
├── prospect_mapper.py
├── provider_factory.py
├── query_generator.py
├── search_provider.py
├── searxng_provider.py
├── service.py
├── url_extractor.py
├── batch/
├── cache/
└── network/
```

---

# 🧱 Design principles

The project is built around several engineering principles.

### Single Responsibility Principle

Each component performs a clearly defined task.

For example:

```text
QueryGenerator       → generates queries
SearchProvider       → performs searches
RelevanceFilter      → evaluates search-result relevance
URLExtractor         → extracts URLs
URLNormalizer        → normalizes URLs
Deduplicator         → removes duplicates
ProspectMapper       → maps URLs to prospects
```

### Dependency Injection

Core services receive their dependencies instead of creating them internally.

This improves:

* testability
* maintainability
* extensibility
* provider replacement

### Interface-based design

External infrastructure is accessed through interfaces where appropriate.

For example:

```python
class SearchProvider(ABC):
    @abstractmethod
    def search(self, query):
        ...
```

This allows the acquisition pipeline to remain independent from the actual search implementation.

### Test Driven Development

The project uses automated tests extensively to validate individual components and integration points.

---

# 🧪 Testing

The project currently has:

```text
114 tests passing
0 tests failing
```

Latest verified state:

```text
114 passed
```

The test suite covers areas including:

* acquisition pipeline
* search providers
* SearXNG provider
* DuckDuckGo provider
* provider factory
* pipeline factory
* relevance filtering
* URL normalization
* deduplication
* retry logic
* rate limiting
* search cache
* SearXNG cache
* error handling
* batch processing
* integration components

Run the complete test suite with:

```bash
pytest -q
```

For verbose output:

```bash
pytest -vv
```

---

# ⚙️ Requirements

Current core stack includes:

* Python 3.13
* SQLAlchemy
* SQLite
* Streamlit
* Google Gemini API
* HTTPX
* BeautifulSoup
* lxml
* Pandas
* OpenPyXL
* Pytest
* DuckDuckGo search integration

SearXNG is used as an external search service and is therefore not installed as a Python dependency of the application.

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Octave2MK/AI-ICP-Qualification-Engine.git
cd AI-ICP-Qualification-Engine
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

---

# 🔐 Environment configuration

Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then configure the required variables.

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_gemini_model
DATABASE_URL=sqlite:///data/icp.db
LLM_PROVIDER=gemini
```

For SearXNG deployments, configure the SearXNG endpoint according to the application's settings.

**Never commit `.env` or API keys to Git.**

---

# 🔍 SearXNG

SearXNG is used as a configurable search provider for the acquisition layer.

The architecture is:

```text
AI ICP Qualification Engine
          ↓
   SearXNGProvider
          ↓
       SearXNG
          ↓
 ┌────────┼────────┐
 ↓        ↓        ↓
DDG     Bing     Qwant
...
```

This architecture separates the prospecting engine from individual search-engine implementations.

A local SearXNG instance can be used during development.

The application communicates with it through its HTTP API.

---

# ▶️ Running the application

The project includes a Streamlit interface.

Run:

```bash
streamlit run app/ui/streamlit_app.py
```

The interface is intended to provide a higher-level entry point for the acquisition and qualification workflow.

---

# 🔄 End-to-end workflow

The complete conceptual workflow is:

```text
                ICP
                 │
                 ▼
          QueryGenerator
                 │
                 ▼
         SearchProvider
        ┌────────┴────────┐
        │                 │
   DuckDuckGo          SearXNG
        │                 │
        └────────┬────────┘
                 ▼
           SearchResult
                 │
                 ▼
        RelevanceFilter
                 │
                 ▼
          URLExtractor
                 │
                 ▼
         URLNormalizer
                 │
                 ▼
          Deduplicator
                 │
                 ▼
        ProspectMapper
                 │
                 ▼
          OSINT Enrichment
                 │
                 ▼
       Profile / ProfileData
                 │
                 ▼
        AI Qualification
                 │
                 ▼
        Result Validation
                 │
                 ▼
        Decision Engine
                 │
                 ▼
         Hybrid Scoring
                 │
                 ▼
            Repository
                 │
                 ▼
              SQLite
```

---

# 🎯 What makes the project different?

The main differentiator is not simply the use of an LLM.

The project combines:

### 1. ICP-first discovery

The search process starts from the customer's ICP rather than from a generic database.

### 2. Search-engine-based OSINT

Instead of depending exclusively on a proprietary lead database, the engine discovers public profiles through search infrastructure.

### 3. Multi-stage filtering

Candidates are progressively reduced:

```text
Search
 ↓
Relevance
 ↓
URL validation
 ↓
Deduplication
 ↓
Enrichment
 ↓
AI qualification
 ↓
Scoring
```

This avoids spending expensive enrichment and LLM resources on obviously irrelevant candidates.

### 4. Hybrid intelligence

The system combines:

```text
Deterministic rules
        +
OSINT data
        +
Semantic/LLM reasoning
        =
Qualification
```

### 5. Provider independence

Search infrastructure is abstracted.

A search provider can be replaced without rewriting the acquisition pipeline.

---

# 📁 Repository structure

```text
AI-ICP-Qualification-Engine/
│
├── app/
│   ├── acquisition/
│   ├── batch/
│   ├── cache/
│   ├── core/
│   ├── database/
│   ├── enrichment/
│   ├── exceptions/
│   ├── pipeline/
│   ├── qualification/
│   ├── reporting/
│   ├── repositories/
│   ├── scoring/
│   ├── ui/
│   ├── factory.py
│   └── main.py
│
├── configs/
│
├── docker/
│
├── tests/
│   ├── acquisition/
│   ├── integration/
│   └── ...
│
├── .env.example
├── .gitignore
├── README.md
├── arborescence.txt
├── requirements.txt
└── requirements-dev.txt
```

---

# 🛣️ Roadmap

Planned improvements include:

* [ ] Complete production-grade SearXNG deployment
* [ ] End-to-end real acquisition testing
* [ ] Parallel search processing
* [ ] Advanced provider fallback
* [ ] PostgreSQL support
* [ ] REST API
* [ ] Multi-LLM support
* [ ] Improved enrichment coverage
* [ ] Dockerized production deployment
* [ ] CI/CD pipeline
* [ ] Authentication
* [ ] Multi-tenant workspaces
* [ ] Advanced prospect analytics
* [ ] Production monitoring and observability

---

# ⚠️ Project status

The project is under active development.

Current verified state:

```text
Architecture              ✅
Acquisition engine        ✅
Search abstraction        ✅
DuckDuckGo provider       ✅
SearXNG provider          ✅
Relevance filtering       ✅
URL extraction            ✅
URL normalization         ✅
Deduplication             ✅
OSINT enrichment          ✅
AI qualification          ✅
Hybrid scoring            ✅
SQLite persistence        ✅
Automated tests           ✅
114 tests passing         ✅
Production hardening      🚧
```

Passing tests demonstrate software correctness against the current automated test suite. They do not by themselves guarantee production reliability against live search engines, external websites, rate limits or changing web structures.

---

# 👤 Author

**Morel Octave**

AI / OSINT / B2B prospecting project.

---

# 📄 License

License information will be added when the project's distribution model is finalized.
