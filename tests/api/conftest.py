import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.dependencies as dependencies
import app.api.job_service as job_service
import app.database.database as database
import app.database.schema as schema
from app.acquisition.acquisition_models import ICP
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.normalizer import URLNormalizer
from app.acquisition.pipeline import AcquisitionPipeline
from app.acquisition.prospect_mapper import ProspectMapper
from app.acquisition.query_generator import QueryGenerator
from app.acquisition.relevance_filter import RelevanceFilter
from app.acquisition.search_provider import MockSearchProvider
from app.acquisition.service import AcquisitionService
from app.acquisition.url_extractor import URLExtractor
from app.enrichment.dto import ProfileData
from app.pipeline.full_pipeline import FullICPWorkflow
from app.pipeline.icp_pipeline import ICPQualificationPipeline
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.service import QualificationService
from app.qualification.validators.result_validator import ResultValidator
from app.repositories.prospect_repository import ProspectRepository
from app.repositories.qualification_repository import QualificationRepository


class _FakeEnricher:
    """Stands in for OSINTEnricher: no real HTTP fetch, deterministic profile."""

    def enrich(self, linkedin_url: str) -> ProfileData:
        return ProfileData(
            linkedin_url=linkedin_url,
            name="",
            headline="Business Coach",
            about="",
            raw_text="Business Coach France",
            clean_text="Business Coach France",
        )


def build_fake_workflow(db) -> FullICPWorkflow:
    """A FullICPWorkflow wired with fakes only at the true I/O boundaries
    (search provider, enrichment fetch, LLM) — everything else (relevance
    filtering, exclusion, pre-filter, decision, scoring) runs for real, so
    job_service's result serialization is exercised against realistic
    shapes, exactly like tests/test_icp_pipeline.py does for the pipeline
    alone."""
    acquisition_pipeline = AcquisitionPipeline(
        query_generator=QueryGenerator(),
        search_provider=MockSearchProvider(),
        url_extractor=URLExtractor(),
        relevance_filter=RelevanceFilter(),
        normalizer=URLNormalizer(),
        deduplicator=Deduplicator(),
        prospect_mapper=ProspectMapper(),
    )
    acquisition_service = AcquisitionService(
        pipeline=acquisition_pipeline,
        repository=ProspectRepository(),
    )

    qualification_service = QualificationService(
        llm=FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )
    qualification_pipeline = ICPQualificationPipeline(
        qualification_service=qualification_service,
        qualification_repository=QualificationRepository(),
    )

    return FullICPWorkflow(
        acquisition_service=acquisition_service,
        osint_enricher=_FakeEnricher(),
        qualification_pipeline=qualification_pipeline,
    )


def failing_workflow_factory(db):
    class _AlwaysFailsAcquisition:
        def acquire(self, db, icp: ICP):
            raise RuntimeError("boom")

    return FullICPWorkflow(
        acquisition_service=_AlwaysFailsAcquisition(),
        osint_enricher=_FakeEnricher(),
        qualification_pipeline=None,
    )


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


@pytest.fixture
def client(monkeypatch, test_engine):
    test_session_local = sessionmaker(
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        bind=test_engine,
    )

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(schema, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", test_session_local)
    monkeypatch.setattr(dependencies, "SessionLocal", test_session_local)
    monkeypatch.setattr(job_service, "SessionLocal", test_session_local)
    monkeypatch.setattr(job_service, "create_full_workflow", build_fake_workflow)

    from app.api.main import app as fastapi_app

    with TestClient(fastapi_app) as test_client:
        yield test_client
