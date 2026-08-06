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
            progress_callback(
                5,
                "Recherche des prospects..."
            )

        prospects = self.acquisition_service.acquire(
            db,
            icp,
        )

        if progress_callback:
            progress_callback(
                20,
                f"{len(prospects)} prospects trouvés"
            )

        results = []
        total = len(prospects)


        for index, prospect in enumerate(
            prospects,
            start=1,
        ):


            if progress_callback:

                percent = 20 + int(
                    (index / total) * 75
                )

                progress_callback(
                    percent,
                    f"Traitement du prospect {index}/{total}"
                )

            try:

                profile = (
                    self.osint_enricher.enrich(
                        prospect.linkedin_url
                    )
                )


                qualification = (
                    self.qualification_pipeline.run(
                        db,
                        prospect,
                        profile,
                    )
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
            progress_callback(
                100,
                "Workflow terminé"
            )


        return results