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

    def run(
        self,
        db,
        icp,
        progress_callback=None,
    ):
        if progress_callback:
            progress_callback(5, "Recherche des prospects...")

        prospects = self.acquisition_service.acquire(db, icp)

        if progress_callback:
            progress_callback(
                20,
                f"{len(prospects)} prospects trouvés",
            )

        results = []
        total = len(prospects)
        qualification_icp = ICPMapper.to_definition(icp)

        for index, prospect in enumerate(prospects, start=1):
            if progress_callback:
                percent = 20 + int((index / total) * 75) if total else 95
                progress_callback(
                    percent,
                    f"Traitement du prospect {index}/{total}",
                )

            try:
                profile = self.osint_enricher.enrich(
                    prospect.linkedin_url
                )

                # L'enrichissement distant peut être incomplet ou bloqué
                # (notamment sur LinkedIn). On conserve donc les signaux
                # fiables obtenus lors de l'acquisition afin que le pré-filtre
                # et le LLM puissent toujours exploiter le résultat de recherche.
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

                qualification = self.qualification_pipeline.run(
                    db,
                    prospect,
                    profile,
                    qualification_icp,
                )

                results.append(
                    {
                        "prospect": prospect,
                        "profile": profile,
                        "qualification": qualification,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "prospect": prospect,
                        "error": str(exc),
                    }
                )

        if progress_callback:
            progress_callback(100, "Workflow terminé")

        return results
