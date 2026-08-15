# Docker

## Overview

The project can run as two Docker services:

```text
Browser
  ↓
Streamlit (ai_icp_app :8501)
  ↓ HTTP
SearXNG (ai_icp_searxng :8080)
```

SQLite data is stored in a named Docker volume so the application container can be recreated without losing the local database.

## Prerequisites

- Docker Desktop with Docker Compose
- A Gemini API key for AI qualification

No Python installation is required on the host when the application is run entirely through Docker.

## First setup

From the repository root, create the local SearXNG configuration from the committed template:

```powershell
Copy-Item docker/settings.yml.example docker/settings.yml
```

Open `docker/settings.yml` and replace `CHANGE_ME_TO_A_RANDOM_SECRET` with a random secret value. `docker/settings.yml` is intentionally ignored by Git because it contains the local SearXNG secret.

Create `.env` from the project template and add the Gemini key:

```powershell
Copy-Item .env.example .env
```

Set at least:

```text
GEMINI_API_KEY=your_key_here
```

## Build and start

```powershell
docker compose -f docker/docker-compose.yml up -d --build
```

The compose file starts:

- `ai_icp_app`: Streamlit application
- `ai_icp_searxng`: SearXNG search service

Check status:

```powershell
docker compose -f docker/docker-compose.yml ps
```

Open Streamlit at:

```text
http://localhost:8501
```

SearXNG remains available only on the local host at:

```text
http://localhost:8080
```

The application container does **not** use `localhost:8080` for SearXNG. Inside the Docker network it uses:

```text
http://searxng:8080
```

This is configured by `SEARXNG_BASE_URL` in Compose.

## Logs

Application:

```powershell
docker compose -f docker/docker-compose.yml logs -f app
```

SearXNG:

```powershell
docker compose -f docker/docker-compose.yml logs -f searxng
```

## Stop / restart

```powershell
docker compose -f docker/docker-compose.yml down
```

Start again without rebuilding:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

The named `icp_data` volume is preserved by `down`, so the SQLite database remains available.

To intentionally remove the persisted database as well:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

## Configuration model

The host `.env` supplies secrets and runtime values such as `GEMINI_API_KEY`. They are passed to the application container through Compose and are not copied into the Docker image.

The application container uses:

```text
SEARCH_PROVIDER=searxng
SEARXNG_BASE_URL=http://searxng:8080
DATABASE_URL=sqlite:////data/icp.db
LLM_PROVIDER=gemini
```

The database path is mounted through the `icp_data` named volume.

## For another user / another PC

A user can clone the repository, install Docker Desktop, create `docker/settings.yml` from the example, configure `.env`, and run:

```powershell
docker compose -f docker/docker-compose.yml up -d --build
```

The same application image is then built locally from the repository. The user does not need to install Python dependencies manually.

The first build requires internet access to download the Python base image and Python packages. Runtime search traffic goes from the application container to the SearXNG container and from SearXNG to its configured upstream search engines.

## Security boundaries

- Streamlit is bound to `127.0.0.1:8501` by default.
- SearXNG is bound to `127.0.0.1:8080` by default.
- The SearXNG secret is kept in the ignored local `docker/settings.yml` file.
- The Gemini API key is supplied through the environment and is not baked into the image.
- The SQLite database is persisted in a Docker-managed volume rather than inside the application image.

These bindings are intentionally suitable for local use. They should not be treated as a production internet-facing deployment configuration.
