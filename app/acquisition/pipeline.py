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
    logger = get_logger(
        "AcquisitionPipeline"
    )
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


    def run(
        self,
        icp: ICP
    ) -> list[ProspectCandidate]:
        all_results = []

        # 1. Génération des requêtes
        queries = (
            self.query_generator.generate(icp)
        )

        # 2. Recherche
        for query in queries:
            try:
                self.logger.info(
                    "Executing search query: %s",
                    query.text,
                )

                results = (
                    self.search_provider.search(query)
                )

                all_results.extend(results)

                print("\nQUERY:", query.text)
                print("SEARCH RESULTS:", len(results))

                for r in results[:3]:
                    print(r.url)
                    print(r.title)
            except Exception as exc:

                self.logger.error(
                    "Search failed for query %s: %s",
                    query.text,
                    exc,
                )
                continue

        # 3. Filtrage de pertinence
        relevant_results = []

        for result in all_results:
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
            "Relevance filter: %s/%s results passed.",
            len(relevant_results),
            len(all_results),
        )

        # 4. Extraction des URLs LinkedIn

        urls = (
            self.url_extractor.extract(relevant_results)
        )

        # 5. Normalisation
        normalized_urls = []

        for url in urls:
            normalized_urls.append(
                self.normalizer.normalize(url)
            )
            print("\nNORMALIZED URLS:", len(normalized_urls))
            for url in normalized_urls[:5]:
                print(url)

        # 6. Déduplication
        clean_urls = (
            self.deduplicator.deduplicate(
                normalized_urls
            )
        )
        print("\nDEDUPLICATED URLS:", len(clean_urls))

        for url in clean_urls[:5]:
            print(url)
        return clean_urls

    def run_and_map(
            self,
            icp: ICP
    ):
        urls = self.run(icp)
        prospects = []
        for url in urls:
            prospects.append(
                self.prospect_mapper.map(url)
            )
        return prospects



