from app.pipeline.full_pipeline import FullICPWorkflow

from app.acquisition.service import (
    AcquisitionService,
    create_acquisition_pipeline,
)

from app.repositories.prospect_repository import (
    ProspectRepository,
)


from app.enrichment.enrichment_service import (
    EnrichmentService,
)

from app.enrichment.osint_enricher import (
    OSINTEnricher,
)

from app.enrichment.page_fetcher import (
    PageFetcher,
)

from app.enrichment.profile_extractor import (
    ProfileExtractor,
)

from app.enrichment.text_cleaner import (
    TextCleaner,
)


from app.pipeline.icp_pipeline import (
    ICPQualificationPipeline,
)

from app.qualification.service import (
    QualificationService,
)


from app.qualification.llm.prompts import (
    PromptBuilder,
)

from app.qualification.parsers.json_parser import (
    JsonParser,
)

from app.qualification.validators.result_validator import (
    ResultValidator,
)


from app.qualification.llm.factory import LLMFactory

from app.repositories.qualification_repository import (
    QualificationRepository,
)



def create_full_workflow(db):

    # ==========================
    # Acquisition
    # ==========================

    acquisition_pipeline = (
        create_acquisition_pipeline()
    )

    acquisition_service = (
        AcquisitionService(
            pipeline=acquisition_pipeline,
            repository=ProspectRepository(),
        )
    )

    # ==========================
    # Enrichment OSINT
    # ==========================

    enrichment_service = (
        EnrichmentService(
            fetcher=PageFetcher(),
            extractor=ProfileExtractor(),
            cleaner=TextCleaner(),
        )
    )

    osint_enricher = (
        OSINTEnricher(
            enrichment_service
        )
    )

    # ==========================
    # Qualification
    # ==========================

    qualification_service = (
        QualificationService(
            llm = LLMFactory.create(),
            prompt_builder=PromptBuilder(),
            parser=JsonParser(),
            validator=ResultValidator(),
        )
    )

    qualification_pipeline = (
        ICPQualificationPipeline(
            qualification_service=qualification_service,
            qualification_repository=QualificationRepository(),
        )
    )

    # ==========================
    # Workflow complet
    # ==========================

    return FullICPWorkflow(
        acquisition_service=acquisition_service,
        osint_enricher=osint_enricher,
        qualification_pipeline=qualification_pipeline,
    )