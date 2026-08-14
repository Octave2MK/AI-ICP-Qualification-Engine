# Development Guide

## Project principles

The project follows a modular architecture with explicit dependencies, separation of concerns, interfaces around external infrastructure and extensive automated testing.

When modifying the acquisition or qualification pipeline, preserve the dynamic ICP contract. Avoid reintroducing a hard-coded ICP name or business-specific assumptions into reusable pipeline components.

## Safe change workflow

1. Inspect the existing implementation and its tests.
2. Identify the public contract of the component being changed.
3. Add or update focused tests first when possible.
4. Make the smallest compatible implementation change.
5. Run the focused tests.
6. Run the full suite with `pytest -q`.
7. Run a real local workflow when the change affects search, enrichment, Gemini, Docker or Streamlit.
8. Only then commit and push.

## Important contracts

### Acquisition

`SearchResult` carries `title`, `url` and `snippet`.

`ProspectCandidate` carries `url`, `title` and `snippet`.

`ProspectMapper` is responsible for converting the candidate into the persistence model. It should not leak search-engine-specific suffixes such as `- LinkedIn` into the stored job title.

### ICP

The UI builds an `ICP` dynamically. Qualification receives an `ICPDefinition` dynamically. Do not replace this with a fixed `business_coach` value.

`required_keywords` are interpreted as alternative relevant terms by the pre-filter: at least one required keyword must match when the list is non-empty. `forbidden_keywords` remain exclusion signals.

### Qualification cache

Qualification cache entries are keyed by prospect and ICP fingerprint. Never reuse a qualification generated for one ICP as the qualification for another ICP.

### Confidence

`minimum_confidence` belongs to the current ICP and is passed into the decision layer. A qualification below that threshold must not be treated as a normal positive decision.

## Search infrastructure

The application supports DuckDuckGo and SearXNG providers. SearXNG is local development infrastructure and is configured in `docker/settings.yml` and `docker/docker-compose.yml`.

The host mapping is deliberately restricted to:

```text
127.0.0.1:8080:8080
```

Do not expose the local development SearXNG instance publicly without deliberately changing the security configuration.

## CI

GitHub Actions runs the non-integration pytest suite on Python 3.13 for pushes and pull requests targeting `main`.

External integration tests are excluded from the default CI run because they may require network services, API keys or quotas.

## Documentation policy

Keep the README focused on project identity, architecture, installation, usage and current status. Put detailed operational and architectural information in `docs/` so the README does not become a maintenance bottleneck.

Whenever behaviour changes in a user-visible way, update the relevant documentation and tests in the same change.
