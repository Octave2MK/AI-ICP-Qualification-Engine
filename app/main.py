from app.database.database import (
    SessionLocal,
    Base,
    engine
)

from app.acquisition.acquisition_models import ICP

from app.acquisition.pipeline import AcquisitionPipeline

from app.acquisition.service import AcquisitionService

from app.acquisition.query_generator import QueryGenerator

from app.acquisition.search_provider import MockSearchProvider

from app.acquisition.url_extractor import URLExtractor

from app.acquisition.normalizer import URLNormalizer

from app.acquisition.deduplicator import Deduplicator

from app.acquisition.prospect_mapper import ProspectMapper

from app.repositories.prospect_repository import ProspectRepository

from app.reporting.acquisition_report import AcquisitionReport



def main():

    # Création des tables si nécessaire

    Base.metadata.create_all(
        bind=engine
    )


    db = SessionLocal()


    try:

        # Construction du pipeline acquisition

        pipeline = AcquisitionPipeline(

            query_generator=QueryGenerator(),

            search_provider=MockSearchProvider(),

            url_extractor=URLExtractor(),

            normalizer=URLNormalizer(),

            deduplicator=Deduplicator(),

            prospect_mapper=ProspectMapper()

        )


        repository = ProspectRepository(
            db
        )


        service = AcquisitionService(
            pipeline,
            repository
        )


        # Définition de l'ICP cible

        icp = ICP(

            job_titles=[
                "Business Coach"
            ],

            countries=[
                "France"
            ]

        )


        # Lancement acquisition

        prospects = service.acquire(
            icp
        )

        report = AcquisitionReport()

        output = report.generate(
            prospects,
            icp
        )

        print(output)


    finally:

        db.close()



if __name__ == "__main__":
    main()