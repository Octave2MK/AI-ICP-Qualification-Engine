from app.qualification.parsers.json_parser import JsonParser
from app.qualification.dto import QualificationResult


def test_parse_valid_json():

    response = """
    {
        "profession": "Business Coach",
        "sector": "Coaching",
        "target_market": "B2B",
        "offer_detected": true,
        "authority_signals": [
            "Publications LinkedIn"
        ],
        "content_signals": [
            "Posts réguliers"
        ],
        "commercial_signals": [
            "Programme de coaching"
        ],
        "icp_match": true,
        "confidence": 0.9,
        "evidence": [
            "Aide les entreprises"
        ],
        "exclusion_reason": null
    }
    """

    result = JsonParser().parse(response)

    assert isinstance(result, QualificationResult)

    assert result.profession == "Business Coach"

    assert result.icp_match is True

    assert result.confidence == 0.9


import pytest

from app.qualification.parsers.json_parser import JsonParser
from app.qualification.exceptions import InvalidQualificationError


def test_parse_invalid_json():

    with pytest.raises(InvalidQualificationError):
        JsonParser().parse(
            "ceci n'est pas du json"
        )