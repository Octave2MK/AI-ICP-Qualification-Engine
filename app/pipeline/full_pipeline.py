from app.qualification.icp.icp_mapper import ICPMapper
from app.enrichment.osint_enricher import OSINTEnricher
from app.pipeline.icp_pipeline import ICPQualificationPipeline


class FullICPWorkflow:
    def __init__(
        self,
        acquisition_service,
        osint_enricher: OSINTEnricher,
        qualification_pipeline: ICPQualificationPipeline,
    ):
        self.acquisition_service = acquisition_service
        self.osint_enricher = osint_enricher
        self.qualification_pipeline = qualification_pipeline

    def run(self, db, icp, progress_callback=None):
        if progress_callback:
            progress_callback(5, "Recherche des prospects...")

        prospects = self.acquisition_service.acquire(db, icp)

        if progress_callback:
            progress_callback(20, f"{len(prospects)} prospects trouvés")

        total = len(prospects)
        qualification_icp = ICPMapper.to_definition(icp)
        results = [None] * total
        batch_items = []

        for index, prospect in enumerate(prospects):
            if progress_callback:
                percent = 20 + int(((index + 1) / total) * 35) if total else 55
                progress_callback(
                    percent,
                    f"Enrichissement du prospect {index + 1}/{total}",
                )

            try:
                profile = self.osint_enricher.enrich(prospect.linkedin_url)

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

                batch_items.append((index, prospect, profile))
            except Exception as exc:
                results[index] = {
                    "prospect": prospect,
                    "error": str(exc),
                }

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
                    results[index] = {
                        "prospect": prospect,
                        "profile": profile,
                        "error": str(exc),
                    }

        if progress_callback:
            progress_callback(95, "Qualification terminée")
            progress_callback(100, "Workflow terminé")

        return [result for result in results if result is not None]
