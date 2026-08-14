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

                # L'enrichissement distant peut être incomplet ou bloqué
                # (notamment sur LinkedIn). On conserve les signaux fiables
                # obtenus lors de l'acquisition.
                profile.acquisition_title = getattr(
                    prospect,
                    "fullname",
                    getattr(profile, "name", "") or "",
                ) or ""
                profile.acquisition_snippet = getattr(
                    prospect,
                    "job_title",
                    getattr(profile, "headline", "") or "",
                ) or ""

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
