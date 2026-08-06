from app.acquisition.service import AcquisitionService
from app.enrichment.enrichment_service import EnrichmentService
from app.pipeline.icp_pipeline import ICPQualificationPipeline


class ICPWorkflow:

    def __init__(
        self,
        acquisition_service: AcquisitionService,
        enrichment_service: EnrichmentService,
        qualification_pipeline: ICPQualificationPipeline,
    ):

        self.acquisition_service = acquisition_service
        self.enrichment_service = enrichment_service
        self.qualification_pipeline = qualification_pipeline


    def run(
        self,
        db,
        icp,
    ):

        prospects = (
            self.acquisition_service.acquire(
                icp
            )
        )


        results = []


        for prospect in prospects:

            try:

                profile = (
                    self.enrichment_service.enrich(
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
                        "result": qualification,
                    }
                )


            except Exception as exc:

                results.append(
                    {
                        "prospect": prospect,
                        "error": str(exc),
                    }
                )


        return results