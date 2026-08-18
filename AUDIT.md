# Audit technique — AI ICP Qualification Engine

**Date de l'audit :** 2026-08-16
**Périmètre :** intégralité du dépôt `c:/AI-ICP` (code applicatif `app/`, tests `tests/`, configuration Docker, CI, documentation)
**Méthode :** revue statique du code source, exécution de la suite de tests, vérification manuelle des points de risque identifiés (SSRF, injection de prompt, code mort, gestion des secrets)

## Résumé exécutif

L'application est un moteur de sourcing et qualification de prospects B2B (recherche web → filtrage → enrichissement OSINT → qualification LLM via Gemini → scoring → persistance SQLite → UI Streamlit). L'architecture annoncée (Clean Architecture, injection de dépendances, interfaces) est **globalement réelle et bien appliquée**, pas seulement cosmétique : les fournisseurs de recherche, le LLM et le fetcher d'enrichissement sont tous injectés derrière des interfaces et sélectionnés par des factories. La suite de tests (123 tests hors intégration) **passe intégralement** et couvre correctement la logique métier centrale.

Les points faibles principaux sont :
- **Sécurité** : un risque SSRF réel dans le fetcher d'enrichissement (aucune validation d'hôte, aucune limite de taille de réponse), une injection de prompt possible via le contenu scrappé envoyé à Gemini, et deux dépendances non versionnées (`ddgs`, `httpx`).
- **Dette d'architecture** : deux modules de pipeline entièrement morts (`app/pipeline/workflow.py`, `app/qualification/qualification_pipeline.py`) dont le nom prête à confusion avec les modules réellement utilisés, plus un sous-système de configuration ICP statique (`configs/*.json`, `ICPLoader`) qui n'est plus utilisé par le flux réel et contredit le principe « ICP dynamique » mis en avant par le projet.
- **Observabilité** : quasiment aucun logging dans les couches pipeline/qualification/scoring ; en cas d'incident (quota Gemini, échec d'enrichissement en masse), il n'existe aucune trace exploitable en dehors du message d'erreur affiché à l'utilisateur.
- **Qualité opérationnelle** : aucun lint/type-check en CI, aucune mesure de couverture, un seul job CI (Ubuntu / Python 3.13 uniquement), et un piège documentaire (`pytest -q` dans le README déclenche des appels réels à l'API Gemini payante avant même de mentionner la commande d'exclusion des tests d'intégration).

Aucune faille critique (exécution de code arbitraire, injection SQL, secret exposé) n'a été trouvée. Les risques identifiés sont réels mais tous corrigibles avec un effort ciblé et proportionné.

---

## 1. Vue d'ensemble du projet

| | |
|---|---|
| Langage | Python 3.13/3.14 |
| Taille | ~3 500 lignes dans `app/`, 72 fichiers de tests |
| Framework UI | Streamlit |
| Persistance | SQLite via SQLAlchemy 2.0 (ORM uniquement, pas de SQL brut) |
| LLM | Google Gemini (`google-genai`), abstraction `BaseLLM` |
| Recherche | DuckDuckGo (`ddgs`) et SearXNG auto-hébergé, derrière `SearchProvider` |
| Déploiement | Docker Compose (2 services : `app`, `searxng`) |
| CI | GitHub Actions, un seul job (`pytest -q -m "not integration"`) |
| Licence | aucune licence déclarée |

Le flux métier (confirmé par lecture du code, cohérent avec `docs/ARCHITECTURE.md`) :

```
ICP (formulaire Streamlit)
  → QueryGenerator → SearchProvider (DDG/SearXNG)
  → RelevanceFilter → URLExtractor → URLNormalizer → Deduplicator → ProspectMapper
  → OSINT enrichment (PageFetcher → ProfileExtractor → TextCleaner)
  → ICPQualificationPipeline : exclusions → pré-filtre ICP → cache (prospect+ICP fingerprint)
    → qualification LLM (batch) → validation → décision (minimum_confidence) → scoring hybride
  → persistance SQLite → table de résultats Streamlit
```

---

## 2. Sécurité

### 2.1 Constats détaillés (par sévérité)

| # | Sévérité | Localisation | Constat |
|---|---|---|---|
| S1 | **Élevée** | [app/enrichment/page_fetcher.py:25-44](app/enrichment/page_fetcher.py#L25-L44), [app/acquisition/url_extractor.py:11-21](app/acquisition/url_extractor.py#L11-L21) | SSRF potentiel : `URLExtractor` ne fait qu'un test de sous-chaîne `"linkedin.com/in/" in result.url` (pas de vérification d'hôte réel), puis `PageFetcher.fetch()` appelle `requests.get()` sans liste blanche de schéma/hôte, sans blocage des plages privées/loopback/métadonnées cloud (`169.254.169.254`), et avec `allow_redirects=True` non contrôlé après coup. Une URL malveillante glissée dans un résultat de recherche pourrait faire pivoter une requête vers le réseau interne du conteneur. |
| S2 | **Élevée** | [app/enrichment/page_fetcher.py:34-41](app/enrichment/page_fetcher.py#L34-L41) | Aucune limite de taille de réponse (`response.text` charge tout le corps en mémoire, pas de `stream=True` ni de plafond d'octets). Une page malveillante ou un endpoint mal configuré peut provoquer un épuisement mémoire. |
| S3 | **Élevée** | [app/qualification/llm/prompts.py:16-88](app/qualification/llm/prompts.py#L16-L88) | Injection de prompt : le texte scrappé (`profile.clean_text`, `headline`, `about`, titre/snippet du résultat de recherche) est interpolé tel quel dans le prompt envoyé à Gemini, sans délimiteurs ni consignes de traitement « comme donnée non fiable ». Un profil conçu pour cela pourrait manipuler `icp_match`/`confidence`/`exclusion_reason`. La clé API n'entre jamais dans le prompt (pas de risque d'exfiltration de secret), mais le résultat de qualification peut être faussé. |
| S4 | Moyenne | [requirements.txt:1-2](requirements.txt#L1-L2) | `ddgs` et `httpx` sont installés sans version épinglée, contrairement à toutes les autres dépendances → builds non reproductibles et surface d'attaque de la chaîne d'approvisionnement (la version installée en CI/Docker peut changer sans revue à chaque rebuild). |
| S5 | Moyenne | [app/ui/streamlit_app.py:111-113](app/ui/streamlit_app.py#L111-L113) | Le message d'exception brut (`str(exc)`) est affiché directement à l'utilisateur via `st.error()`, ce qui peut exposer des détails internes (chemins, messages d'erreur de bibliothèque/API). |
| S6 | Moyenne | [app/acquisition/duckduckgo_provider.py](app/acquisition/duckduckgo_provider.py) | Contrairement au fournisseur SearXNG, le fournisseur DuckDuckGo n'a aucun `RateLimiter`. `QueryGenerator` peut produire plusieurs variantes de requête par recherche, envoyées sans limitation de débit vers DuckDuckGo. |
| S7 | Moyenne | [app/factory.py:64-72](app/factory.py#L64-L72), [app/ui/workflow_runner.py](app/ui/workflow_runner.py) | Un `RateLimiter` neuf est recréé à chaque exécution du workflow (bouton « Lancer la recherche »). Rien n'empêche un utilisateur de relancer le workflow en boucle : pas de cooldown de session, pas de quota applicatif sur les appels Gemini (facturés) ni sur les appels aux moteurs de recherche externes. |
| S8 | Faible | [Dockerfile](Dockerfile) | Le conteneur applicatif tourne en `root` (pas de directive `USER`), pas de `HEALTHCHECK`. Risque limité mais non conforme aux bonnes pratiques de durcissement de conteneur. |
| S9 | Faible | [docker/settings.yml.example:6-19](docker/settings.yml.example) | Le template SearXNG désactive `limiter` et `botdetection`. Sans danger tant que le port reste lié à `127.0.0.1` (c'est le cas actuellement), mais devient un relais d'abus ouvert si quelqu'un republie le port sur `0.0.0.0` sans revoir cette configuration. |
| S10 | Info | [app/core/logging.py](app/core/logging.py) | Pas de filtre de rédaction de secrets sur le logger. Non exploité aujourd'hui (aucune clé API n'est loguée), mais du texte OSINT potentiellement personnel transite par `logger.debug`/`logger.exception` sans anonymisation. |

### 2.2 Points positifs à noter

- **Aucune injection SQL possible** : `app/repositories/*` et `app/database/models.py` utilisent exclusivement l'ORM SQLAlchemy, aucune concaténation de SQL brut trouvée dans tout le dépôt.
- **Aucun risque XXE** : `lxml` est déclaré en dépendance mais n'est utilisé nulle part pour du parsing XML ; `ProfileExtractor` utilise BeautifulSoup avec le parseur `html.parser`.
- **Aucun `eval`/`exec`/`os.system`/`subprocess`/`pickle`/YAML non sécurisé** dans `app/`.
- **Hygiène des secrets solide** : `.gitignore` exclut correctement `.env`, `docker/settings.yml`, `*.db`, `.streamlit/secrets.toml` ; `.env.example` et `docker/settings.yml.example` ne contiennent que des placeholders (`your_api_key_here`, `CHANGE_ME_TO_A_RANDOM_SECRET`).
- **Clés API jamais loguées** : `GEMINI_API_KEY`/`OPENAI_API_KEY` sont déclarées `repr=False` dans le dataclass `Settings` ([app/core/settings.py:66-79](app/core/settings.py#L66-L79)).
- **Exposition réseau restreinte par défaut** : les deux services Docker (`app`, `searxng`) lient leurs ports sur `127.0.0.1` uniquement dans `docker-compose.yml`.
- **Pas de surface d'injection de formule Excel** : bien que `test_prospects.xlsx/csv` existent à la racine, aucun code d'export (`to_excel`, `to_csv`, `download_button`) n'existe dans `app/` — ce sont de simples fixtures inutilisées, pas une fonctionnalité active.
- **Retry borné** : `app/acquisition/network/retry.py` a un nombre de tentatives maximal fixe, pas de boucle infinie possible.

---

## 3. Architecture et qualité de code

### 3.1 L'injection de dépendances est réelle, pas décorative

`app/factory.py` agit comme une véritable racine de composition : `QualificationService` dépend de l'interface `BaseLLM` ([app/qualification/interfaces.py](app/qualification/interfaces.py)), pas de `GeminiClient` directement ; le client concret est choisi par `LLMFactory` selon `settings.LLM_PROVIDER`. Même schéma pour la recherche (`SearchProvider` → `ProviderFactory`) et l'enrichissement (`BaseFetcher`/`BaseExtractor`/`BaseCleaner`, injectés dans `EnrichmentService`). C'est un point fort réel du projet.

Une seule fuite de couche identifiée : [app/ui/workflow_runner.py:2-11](app/ui/workflow_runner.py#L2-L11) importe directement `SessionLocal`, `Base`, `engine` et `ensure_schema` depuis `app/database/*` et gère lui-même le bootstrap de schéma et le cycle de vie de la session — la couche UI fait ainsi un travail d'infrastructure qui devrait relever de la factory.

### 3.2 Modules morts et nommage trompeur (constat le plus important de cette section)

Quatre fichiers portent des noms proches (« pipeline »), mais deux sont **du code mort** :

| Fichier | Statut | Usage réel |
|---|---|---|
| `app/pipeline/icp_pipeline.py` (`ICPQualificationPipeline`) | ✅ Vivant | Câblé dans `factory.py`, exécute exclusion → pré-filtre → cache → qualification → décision → score |
| `app/pipeline/full_pipeline.py` (`FullICPWorkflow`) | ✅ Vivant | Orchestrateur de bout en bout réellement utilisé par `workflow_runner.py` |
| `app/pipeline/workflow.py` (`ICPWorkflow`) | ❌ **Mort** | N'est importé nulle part en dehors de son propre fichier — vérifié par recherche globale |
| `app/qualification/qualification_pipeline.py` (`QualificationPipeline`) | ❌ **Mort** | N'est importé que par ses propres tests (`tests/qualification/test_qualification_pipeline*.py`) ; entièrement remplacé par `ICPQualificationPipeline` |

Ces deux modules morts possèdent encore leurs propres fichiers de test, qui passent en CI tout en validant du code que l'application ne exécute jamais en production — un faux sentiment de couverture.

Autres éléments de code mort confirmés :
- `SearchProviderError` ([app/acquisition/exceptions.py:1](app/acquisition/exceptions.py#L1)) : classe d'exception définie mais jamais levée ni importée.
- `QualificationRepository.get_by_prospect_id` ([app/repositories/qualification_repository.py:112-130](app/repositories/qualification_repository.py#L112-L130)) : sa propre docstring la qualifie de « legacy », aucun appelant restant.
- `app/qualification/config/icp_loader.py` (`ICPLoader`) et `configs/business_coach.json` / `configs/consultant.json` : uniquement référencés par leurs tests dédiés. Le flux réel construit `ICPDefinition` dynamiquement via `ICPMapper.to_definition()`, jamais via `ICPLoader.load()`. Ce sous-système contredit directement le message du README (« *The pipeline does not hard-code a business_coach ICP* ») — il s'agit visiblement d'un reliquat d'une conception antérieure à ICP statique.

**Recommandation** : supprimer `app/pipeline/workflow.py`, `app/qualification/qualification_pipeline.py`, `SearchProviderError`, la méthode legacy du repository, et évaluer si `ICPLoader`/`configs/*.json` doivent être retirés ou au contraire reconnectés à une fonctionnalité future (import d'ICP depuis un fichier).

### 3.3 Gestion des erreurs

Des exceptions dédiées existent et sont utilisées correctement à leur point d'origine (`PageFetchError`, `SearXNGError`, `LLMError`, `InvalidQualificationError`). Six `except Exception` larges ont été recensés : la plupart sont des décisions délibérées aux frontières du workflow (transformer un échec par prospect en entrée d'erreur plutôt que d'interrompre le batch) et sont défendables. L'exception est [app/acquisition/duckduckgo_provider.py:47](app/acquisition/duckduckgo_provider.py#L47) : un `except Exception:` nu qui avale l'erreur et retourne une liste vide — indiscernable pour l'appelant d'une recherche qui n'a simplement rien trouvé. Ce silence peut masquer des pannes réelles du fournisseur de recherche.

### 3.4 Duplication apparente : fausse alerte

Les modules de scoring (`rules.py` → `scoring_engine.py` → `ai_scoring.py` → `hybrid_scoring.py`) et de normalisation (`profession_normalizer.py`, `sector_normalizer.py` orchestrés par `qualification_normalizer.py`) ne sont **pas** dupliqués : chaque fichier a une responsabilité unique et bien séparée. C'est un exemple de composition à responsabilité unique correctement appliqué, à préserver tel quel.

### 3.5 Configuration

`app/core/settings.py` est un `dataclass` frozen qui lit `os.environ` une seule fois via des valeurs par défaut de champ, avec un singleton `settings` unique — aucune lecture d'environnement dispersée ailleurs dans `app/`. En revanche, il n'y a **aucune validation** : une `GEMINI_API_KEY` vide se résout silencieusement en chaîne vide plutôt que de faire échouer le démarrage avec un message clair. C'est cohérent avec le statut « 🚧 Production hardening » revendiqué par le README.

### 3.6 Points positifs à noter

- Frontière anti-corruption propre entre bornes métier : `ICPMapper` convertit l'`ICP` de la couche acquisition en `ICPDefinition` de la couche qualification, évitant un couplage direct entre les deux domaines.
- Nommage cohérent (snake_case, PascalCase), typage présent et correct dans les modules centraux (`relevance_filter.py`, `service.py`, `icp_pipeline.py`, `icp_definition.py`).
- Aucun commentaire `TODO`/`FIXME`/`XXX` ni bloc de code commenté trouvé dans `app/` — le code actif est propre.
- Aucun fichier ne dépasse 240 lignes ; les fichiers les plus longs (`relevance_filter.py` 239 lignes, `acquisition/pipeline.py` 167 lignes) restent lisibles et à responsabilité unique — pas de découpage nécessaire pour l'instant.

---

## 4. Tests, CI et fiabilité

### 4.1 Exécution de la suite de tests

```
python -m pytest -q -m "not integration"
123 passed, 5 deselected in ~71-107s
```

La suite passe intégralement dans cet environnement après installation des dépendances (`requirements.txt` + `requirements-dev.txt`).

### 4.2 Couverture par module

La correspondance `app/` ↔ `tests/` est globalement bonne mais incomplète :

- **Sans test dédié** : `app/database/schema.py` (exercé seulement indirectement via la fixture SQLite en mémoire), `app/scoring/rules.py` (atteint seulement via `ScoringEngine`), `app/ui/workflow_runner.py` et `app/ui/streamlit_app.py` (0 test direct — seul `tests/ui/test_prospect_view.py` existe pour la couche UI).
- **Convention de rangement incohérente** : les tests d'enrichissement (`test_enrichment_service.py`, `test_page_fetcher.py`, `test_profile_extractor.py`, `test_text_cleaner.py`) sont à plat sous `tests/` au lieu d'un dossier `tests/enrichment/`, contrairement à `acquisition/`, `qualification/`, `pipeline/`.
- **Bien couverts** : `app/acquisition/cache`, `app/acquisition/batch`, `app/acquisition/network` (retry/rate-limiter) ont chacun leur test dédié.

### 4.3 Qualité des tests (échantillon revu)

- `tests/qualification/test_decision_engine.py` : couvre les 4 statuts nominaux mais **pas** le cas limite exact `confidence == minimum_confidence`, ni le chemin `ValueError` documenté dans [app/qualification/decision/decision_engine.py:9-15](app/qualification/decision/decision_engine.py#L9-L15). Quatre tests structurellement identiques sans `@pytest.mark.parametrize`.
- `tests/acquisition/test_retry.py` : un seul scénario (succès après 2 échecs) ; **aucun test de l'épuisement des tentatives**, ni du délai de backoff.
- `tests/acquisition/test_rate_limiter.py` : ne teste que la branche « attente nécessaire », pas la branche « pas d'attente ».
- `app/qualification/llm/fake_llm.py` est une fausse implémentation **statique** (retourne toujours la même réponse) — utile pour vérifier le format JSON, mais ne permet pas de tester le pipeline sous des réponses LLM variées (faible confiance, JSON malformé, exclusion).
- `tests/acquisition/test_pipeline_contract.py` est en revanche un vrai test de contrat : il câble de vrais collaborateurs (`URLExtractor`, `RelevanceFilter`, `Deduplicator`) avec des doubles seulement pour la recherche/génération de requêtes — bon niveau de test comportemental.

### 4.4 Tests d'intégration et risque documentaire

`tests/integration/test_api_key.py`, `test_gemini_real.py`, `test_qualification_gemini.py` appellent la **vraie API Gemini** et sont correctement marqués `@pytest.mark.integration`, donc exclus de la CI. En revanche, `tests/integration/test_gemini_client.py` vit dans le dossier `integration/` mais **n'a pas le marqueur** — il s'exécute donc en CI (sans risque actuellement car il utilise une fausse clé, mais un futur test ajouté ici sans marqueur explicite pourrait silencieusement appeler l'API réelle en CI).

Risque plus important côté documentation : le [README.md:309-313](README.md#L309-L313) présente `pytest -q` (« Run the full suite ») **avant** `pytest -q -m "not integration"` (la commande équivalente à la CI). Un développeur qui suit le README dans l'ordre, avec une `GEMINI_API_KEY` valide dans `.env` (nécessaire au fonctionnement de l'app), déclenchera sans le savoir des appels réels facturés à Gemini.

### 4.5 CI

`.github/workflows/tests.yml` : un seul job, Ubuntu, Python 3.13 uniquement, avec cache pip. Aucune étape de lint ou de vérification de types (aucun `pyproject.toml`, `.flake8`, `mypy.ini`, `ruff.toml` dans le dépôt), aucun rapport de couverture (`requirements-dev.txt` ne contient que `pytest`).

### 4.6 Observabilité

`app/core/logging.py` utilise un `logging.basicConfig` simple, texte brut, sans identifiants de corrélation. Les appels au logger sont concentrés dans 3 fichiers de la couche acquisition (`duckduckgo_provider.py`, `searxng_provider.py`, `acquisition/pipeline.py`) — **`app/pipeline/full_pipeline.py`, `icp_pipeline.py`, et l'ensemble de `app/qualification/`, `app/enrichment/`, `app/scoring/` n'ont aucun appel au logger**. Les erreurs par prospect sont capturées dans les résultats mais jamais loguées, ce qui rend un incident de quota Gemini en production difficile à diagnostiquer autrement que via l'écran Streamlit au moment des faits. Cela confirme fidèlement le statut « à faire » du README pour l'item de roadmap « observability and monitoring ».

### 4.7 Points positifs à noter

- Séparation nette unitaire / intégration via les marqueurs pytest, globalement bien appliquée.
- Isolation des échecs par prospect **et** par batch dans `full_pipeline.py` (lignes 39-114) : un échec d'enrichissement ou un dépassement de quota Gemini sur un batch ne fait pas tomber tout le workflow, conformément à l'avertissement du README sur les erreurs `429 RESOURCE_EXHAUSTED`.
- Fixture SQLite en mémoire (`tests/conftest.py`) pour des tests de base de données rapides et isolés.

---

## 5. Synthèse des recommandations, par priorité

| Priorité | Action | Domaine |
|---|---|---|
| 1 | Valider l'hôte réel des URLs LinkedIn extraites (pas un simple `in`), bloquer les plages d'IP privées/loopback/métadonnées et plafonner la taille de réponse dans `PageFetcher` | Sécurité (S1, S2) |
| 2 | Délimiter clairement le contenu scrappé dans les prompts Gemini et l'étiqueter comme donnée non fiable | Sécurité (S3) |
| 3 | Épingler les versions de `ddgs` et `httpx` dans `requirements.txt` | Sécurité (S4) |
| 4 | Supprimer `app/pipeline/workflow.py`, `app/qualification/qualification_pipeline.py`, `SearchProviderError`, la méthode legacy du repository ; statuer sur le sort de `ICPLoader`/`configs/*.json` | Architecture |
| 5 | Ajouter le marqueur `integration` manquant sur `tests/integration/test_gemini_client.py` et avertir clairement dans le README, avant la commande `pytest -q`, que les tests d'intégration consomment un vrai quota Gemini | Tests/Doc |
| 6 | Ajouter du logging dans les couches pipeline/qualification/enrichment/scoring, au minimum aux points d'échec par lot | Observabilité |
| 7 | Ajouter un job de lint/type-check (ruff + mypy) et un rapport de couverture (`pytest-cov`) à la CI | CI |
| 8 | Ajouter un plafond applicatif (cooldown ou quota par session) sur les relances de workflow depuis l'UI Streamlit | Sécurité (S6, S7) |
| 9 | Ajouter un `USER` non-root et un `HEALTHCHECK` au `Dockerfile` | Déploiement |

## 6. Ce qui fonctionne bien (à préserver)

- Injection de dépendances réelle et cohérente autour des interfaces `SearchProvider`, `BaseLLM`, `BaseFetcher`/`BaseExtractor`/`BaseCleaner`.
- Aucune injection SQL, aucun XXE, aucun `eval`/`exec`, aucune commande shell dynamique.
- Hygiène des secrets exemplaire (`.gitignore`, placeholders, `repr=False`, ports Docker liés à `localhost`).
- Isolation des erreurs par prospect et par batch dans le workflow principal.
- Séparation propre marqueurs unit/intégration en tests, et frontière anti-corruption `ICPMapper` entre acquisition et qualification.
- Suite de tests fonctionnelle et intégralement verte (123/123 hors intégration).

---

*Cet audit a été réalisé par revue statique du code, exécution de la suite de tests et vérification manuelle ciblée des constats les plus sensibles. Il ne remplace pas un test d'intrusion ni une revue de sécurité formelle sur un déploiement en production.*
