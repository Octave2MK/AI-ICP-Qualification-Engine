from urllib.parse import urlparse

from app.acquisition.acquisition_models import (
    ICP,
    ProspectCandidate,
)
from app.acquisition.query_generator import QueryGenerator
from app.acquisition.search_provider import SearchProvider
from app.acquisition.url_extractor import URLExtractor
from app.acquisition.normalizer import URLNormalizer
from app.acquisition.relevance_filter import RelevanceFilter
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.prospect_mapper import ProspectMapper
from app.core.logging import get_logger


class AcquisitionPipeline:
    logger = get_logger("AcquisitionPipeline")

    """
    Pipeline complet d'acquisition OSINT.
    """

    def __init__(
        self,
        query_generator: QueryGenerator,
        search_provider: SearchProvider,
        url_extractor: URLExtractor,
        relevance_filter: RelevanceFilter,
        normalizer: URLNormalizer,
        deduplicator: Deduplicator,
        prospect_mapper: ProspectMapper,
    ):
        self.query_generator = query_generator
        self.search_provider = search_provider
        self.url_extractor = url_extractor
        self.relevance_filter = relevance_filter
        self.normalizer = normalizer
        self.deduplicator = deduplicator
        self.prospect_mapper = prospect_mapper

    def run(self, icp: ICP) -> list[ProspectCandidate]:
        all_results = []

        # 1. Génération des requêtes
        queries = self.query_generator.generate(icp)

        # 2. Recherche
        for query in queries:
            try:
                self.logger.info(
                    "Executing search query: %s",
                    query.text,
                )

                results = self.search_provider.search(query)
                all_results.extend(results)

                self.logger.info(
                    "Search returned %s results for query: %s",
                    len(results),
                    query.text,
                )

            except Exception as exc:
                self.logger.error(
                    "Search failed for query %s: %s",
                    query.text,
                    exc,
                )
                continue

        # 3. Restriction à la source cible avant le scoring.
        linkedin_results = [
            result
            for result in all_results
            if self._is_linkedin_profile(result.url)
        ]

        self.logger.info(
            "LinkedIn profile results: %s/%s",
            len(linkedin_results),
            len(all_results),
        )

        # 4. Filtrage de pertinence
        relevant_results = []

        for result in linkedin_results:
            relevance = self.relevance_filter.evaluate(
                ProspectCandidate(
                    url=result.url,
                    title=result.title,
                    snippet=result.snippet,
                ),
                icp,
            )

            if relevance.passed:
                relevant_results.append(result)

        self.logger.info(
            "Relevance filter: %s/%s LinkedIn results passed.",
            len(relevant_results),
            len(linkedin_results),
        )

        # 5. Extraction des candidats LinkedIn
        candidates = self.url_extractor.extract(relevant_results)

        self.logger.info(
            "Extracted LinkedIn profiles: %s",
            len(candidates),
        )

        # 6. Normalisation : le contrat reste ProspectCandidate.
        normalized_candidates = [
            self.normalizer.normalize(candidate)
            for candidate in candidates
        ]

        self.logger.info(
            "Normalized LinkedIn profiles: %s",
            len(normalized_candidates),
        )

        # 7. Déduplication : le contrat reste ProspectCandidate.
        deduplicated_candidates = self.deduplicator.deduplicate(
            normalized_candidates
        )

        self.logger.info(
            "Deduplicated LinkedIn profiles: %s",
            len(deduplicated_candidates),
        )

        # 8. Respecter la cible demandée par l'utilisateur après toutes les
        # étapes de qualité. Une recherche peut naturellement retourner moins
        # de profils que demandé : on ne fabrique jamais de prospects.
        max_prospects = getattr(icp, "max_prospects", None)
        if max_prospects is not None:
            if not isinstance(max_prospects, int) or max_prospects < 1:
                raise ValueError("max_prospects must be a positive integer")
            deduplicated_candidates = deduplicated_candidates[:max_prospects]

        return deduplicated_candidates

    @staticmethod
    def _is_linkedin_profile(url: str) -> bool:
        """Return True only for public LinkedIn profile URLs. Validates the
        actual host (linkedin.com or a subdomain, e.g. fr.linkedin.com)
        rather than a substring match, so a spoofed host embedding
        "linkedin.com/in/" in its path cannot be treated as a profile URL."""
        if not url:
            return False

        parsed = urlparse(url.strip())
        hostname = (parsed.hostname or "").lower()
        is_linkedin_host = (
            hostname == URLExtractor.ROOT_HOST
            or hostname.endswith("." + URLExtractor.ROOT_HOST)
        )

        return is_linkedin_host and URLExtractor.PROFILE_PATH_PREFIX in parsed.path

    def run_and_map(self, icp: ICP):
        candidates = self.run(icp)
        prospects = []

        for candidate in candidates:
            prospects.append(
                self.prospect_mapper.map(candidate)
            )

        return prospects
