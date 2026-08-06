import json

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