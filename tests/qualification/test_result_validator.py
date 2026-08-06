from app.qualification.dto import QualificationResult
from app.qualification.validators.result_validator import ResultValidator


def test_valid_result_passes():
    validator = ResultValidator()

    result = QualificationResult(
        profession="Business Coach",
        sector="Consulting",
        target_market="B2B",
        offer_detected=True,
        authority_signals=["Speaker"],
        content_signals=["Posts weekly"],
        commercial_signals=["Book a call"],
        icp_match=True,
        confidence=0.91,
        evidence=["Headline mentions coaching"],
    )

    validator.validate(result)

import pytest

from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError
from app.qualification.validators.result_validator import ResultValidator


def test_confidence_must_be_between_zero_and_one():
    validator = ResultValidator()

    result = QualificationResult(
        profession="Coach",
        sector="Business",
        target_market="B2B",
        offer_detected=True,
        confidence=1.5,
    )

    with pytest.raises(InvalidQualificationError):
        validator.validate(result)

import pytest

from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError
from app.qualification.validators.result_validator import ResultValidator


def test_profession_cannot_be_empty():
    validator = ResultValidator()

    result = QualificationResult(
        profession="",
        sector="Business",
        target_market="B2B",
        offer_detected=True,
    )

    with pytest.raises(InvalidQualificationError):
        validator.validate(result)

import pytest

from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError
from app.qualification.validators.result_validator import ResultValidator


def test_sector_cannot_be_empty():
    validator = ResultValidator()

    result = QualificationResult(
        profession="Coach",
        sector="",
        target_market="B2B",
        offer_detected=True,
    )

    with pytest.raises(InvalidQualificationError):
        validator.validate(result)

import pytest

from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError
from app.qualification.validators.result_validator import ResultValidator


def test_evidence_required_when_icp_match():
    validator = ResultValidator()

    result = QualificationResult(
        profession="Coach",
        sector="Business",
        target_market="B2B",
        offer_detected=True,
        icp_match=True,
        confidence=0.95,
        evidence=[],
    )

    with pytest.raises(InvalidQualificationError):
        validator.validate(result)