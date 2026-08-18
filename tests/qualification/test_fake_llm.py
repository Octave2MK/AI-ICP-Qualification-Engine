import json

import pytest

from app.qualification.llm.fake_llm import FakeLLM


def test_fake_llm_returns_valid_json():
    llm = FakeLLM()

    response = llm.analyze("anything")

    data = json.loads(response)

    assert data["profession"] == "Business Coach"
    assert data["icp_match"] is True

def test_fake_llm_ignores_input():
    llm = FakeLLM()

    first = llm.analyze("abc")

    second = llm.analyze("xyz")

    assert first == second


def test_fake_llm_can_be_configured_with_a_custom_dict_response():
    llm = FakeLLM(response={"profession": "Consultant", "confidence": 0.3})

    data = json.loads(llm.analyze("anything"))

    assert data == {"profession": "Consultant", "confidence": 0.3}


def test_fake_llm_can_be_configured_with_a_raw_string_response():
    llm = FakeLLM(response="not valid json")

    assert llm.analyze("anything") == "not valid json"


def test_fake_llm_can_be_configured_to_raise():
    llm = FakeLLM(response=RuntimeError("quota exhausted"))

    with pytest.raises(RuntimeError, match="quota exhausted"):
        llm.analyze("anything")