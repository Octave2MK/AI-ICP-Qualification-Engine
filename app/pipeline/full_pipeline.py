from app.qualification.icp.icp_mapper import ICPMapper
from app.enrichment.interfaces.batch_enricher import BaseBatchEnricher
from app.enrichment.osint_enricher import OSINTEnricher
from app.pipeline.icp_pipeline import ICPQualificationPipeline
from app.core.logging import get_logger

logger = get_logger(__name__)


class FullICPWorkflow:
    def __init__(
        self,
        acquisition_service,
        osint_enricher: OSINTEnricher | BaseBatchEnricher,
        qualification_pipeline: ICPQualificationPipeline,
    ):
        self.acquisition_service = acquisition_service
        self.osint_enricher = osint_enricher
        self.qualification_pipeline = qualification_pipeline

    def run(self, db, icp, progress_callback=None):
        if progress_callback:
            progress_callback(5, "Recherche des prospects..., veillez patienter")

        prospects = self.acquisition_service.acquire(db, icp)

        if progress_callback:
            progress_callback(20, f"{len(prospects)} prospects trouvés")

        total = len(prospects)
        qualification_icp = ICPMapper.to_definition(icp)
        results: list[dict | None] = [None] * total

        if isinstance(self.osint_enricher, BaseBatchEnricher):
            batch_items = self._enrich_batch(
                self.osint_enricher, prospects, results, progress_callback
            )
        else:
            batch_items = self._enrich_one_by_one(
                self.osint_enricher, prospects, results, total, progress_callback
            )

        # New production path: enrich first, then qualify all pending profiles
        # in one LLM batch. Keep the old per-profile path as a compatibility
        # fallback for lightweight/fake pipeline implementations used by tests.
        if hasattr(self.qualification_pipeline, "run_batch") and batch_items:
            try:
                qualified = self.qualification_pipeline.run_batch(
                    db,
                    [(prospect, profile) for _, prospect, profile in batch_items],
                    qualification_icp,
                )

                for (index, prospect, profile), qualification in zip(
                    batch_items,
                    qualified,
                ):
                    results[index] = {
                        "prospect": prospect,
                        "profile": profile,
                        "qualification": qualification,
                    }
            except Exception as exc:
                # Preserve per-prospect output shape even when the whole batch
                # fails (for example because Gemini quota is exhausted).
                logger.warning(
                    "Batch qualification failed for %d prospect(s), "
                    "recording as error: %s",
                    len(batch_items),
                    exc,
                )
                for index, prospect, profile in batch_items:
                    results[index] = {
                        "prospect": prospect,
                        "profile": profile,
                        "error": str(exc),
                    }
        else:
            for index, prospect, profile in batch_items:
                try:
                    qualification = self.qualification_pipeline.run(
                        db,
                        prospect,
                        profile,
                        qualification_icp,
                    )
                    results[index] = {
                        "prospect": prospect,
                        "profile": profile,
                        "qualification": qualification,
                    }
                except Exception as exc:
                    logger.warning(
                        "Qualification failed for prospect %s, recording as error: %s",
                        getattr(prospect, "id", None),
                        exc,
                    )
                    results[index] = {
                        "prospect": prospect,
                        "profile": profile,
                        "error": str(exc),
                    }

        if progress_callback:
            progress_callback(95, "Qualification terminée")
            progress_callback(100, "Workflow terminé")

        return [result for result in results if result is not None]

    def _enrich_one_by_one(
        self, enricher: OSINTEnricher, prospects, results, total, progress_callback
    ):
        """Legacy path: one fetch/extract call per prospect (BeautifulSoup
        engine, or any BaseFetcher/BaseExtractor-based enricher)."""
        batch_items = []

        for index, prospect in enumerate(prospects):
            if progress_callback:
                percent = 20 + int(((index + 1) / total) * 35) if total else 55
                progress_callback(
                    percent,
                    f"Enrichissement du prospect {index + 1}/{total}, veillez patienter",
                )

            try:
                profile = enricher.enrich(prospect.linkedin_url)
                self._apply_acquisition_fallback(prospect, profile)
                batch_items.append((index, prospect, profile))
            except Exception as exc:
                logger.warning(
                    "Enrichment failed for prospect %s, recording as error: %s",
                    getattr(prospect, "id", None),
                    exc,
                )
                results[index] = {
                    "prospect": prospect,
                    "error": str(exc),
                }

        return batch_items

    def _enrich_batch(
        self, enricher: BaseBatchEnricher, prospects, results, progress_callback
    ):
        """Batch path: one call enriches every prospect's URL in a single
        operation (e.g. ScrapyBatchEnricher). A prospect whose URL is absent
        from the returned mapping is treated as an individual enrichment
        failure, exactly like the per-prospect try/except in the legacy
        path — it does not fail the whole batch."""
        if progress_callback:
            progress_callback(25, "Enrichissement des prospects (lot)...")

        urls = [prospect.linkedin_url for prospect in prospects]

        try:
            profiles_by_url = enricher.enrich_many(urls)
        except Exception as exc:
            logger.warning(
                "Batch enrichment failed for %d prospect(s), recording as error: %s",
                len(prospects),
                exc,
            )
            profiles_by_url = {}

        batch_items = []

        for index, prospect in enumerate(prospects):
            profile = profiles_by_url.get(prospect.linkedin_url)

            if profile is None:
                results[index] = {
                    "prospect": prospect,
                    "error": "Enrichment failed or produced no profile for this URL.",
                }
                continue

            self._apply_acquisition_fallback(prospect, profile)
            batch_items.append((index, prospect, profile))

        return batch_items

    @staticmethod
    def _apply_acquisition_fallback(prospect, profile):
        # LinkedIn enrichment can be incomplete. Acquisition already
        # contains reliable search-result identity/job-title signals;
        # expose them through the normal profile fields so the
        # qualification prompt can use them without requiring a
        # separate enrichment-specific path.
        acquired_name = getattr(prospect, "fullname", "") or ""
        acquired_job_title = getattr(prospect, "job_title", "") or ""

        profile.name = profile.name or acquired_name
        profile.headline = profile.headline or acquired_job_title
        profile.acquisition_title = (
            acquired_name or getattr(profile, "name", "") or ""
        )
        profile.acquisition_snippet = (
            acquired_job_title or getattr(profile, "headline", "") or ""
        )
