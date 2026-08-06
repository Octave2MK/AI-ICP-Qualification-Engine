AI ICP Qualification Engine

AI-powered B2B prospect sourcing and qualification engine using OSINT, LinkedIn and Large Language Models.

Features
Google/DuckDuckGo OSINT sourcing
LinkedIn profile enrichment
AI qualification using Gemini
Hybrid ICP scoring
SQLite persistence
Qualification cache
Streamlit interface
CSV & Excel export
Clean Architecture
Dependency Injection
Test Driven Development
Workflow
Acquisition

↓

URL Normalization

↓

Deduplication

↓

OSINT Enrichment

↓

Pre-filter

↓

Gemini Qualification

↓

Decision Engine

↓

Hybrid Scoring

↓

Persistence

↓

Dashboard
Tech Stack
Python 3.13
Streamlit
SQLAlchemy
Gemini API
DuckDuckGo Search
BeautifulSoup
SQLite
Pandas
Pytest
Installation
git clone ...

cd AI-ICP-Qualification-Engine

python -m venv .venv

pip install -r requirements.txt

Créer le fichier .env

cp .env.example .env

Puis renseigner :

GEMINI_API_KEY=...

Lancer l'application

streamlit run app/ui/streamlit_app.py
Tests
pytest
Project Structure

(Arborescence)

Architecture
Presentation

↓

Application

↓

Domain

↓

Infrastructure
Current capabilities

✅ Acquisition

✅ Enrichment

✅ Qualification

✅ Hybrid scoring

✅ SQLite cache

✅ Streamlit UI

Roadmap
API REST
PostgreSQL
Multi-LLM support
Parallel processing
Docker
CI/CD
User authentication
Multi-tenant workspaces
Author
Morel Octave