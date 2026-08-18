import json

from app.qualification.interfaces import BaseLLM


DEFAULT_RESPONSE = {
    "profession": "Business Coach",
    "sector": "Consulting",
    "target_market": "B2B",
    "offer_detected": True,
    "authority_signals": ["Speaker"],
    "content_signals": ["Publishes on LinkedIn"],
    "commercial_signals": ["Call booking link"],
    "icp_match": True,
    "confidence": 0.95,
    "evidence": ["Headline mentions business coaching"],
    "exclusion_reason": None,
}


class FakeLLM(BaseLLM):
    """LLM factice pour des tests déterministes.

    Par défaut, retourne toujours la même réponse qualifiante (comportement
    historique, inchangé). Un appelant peut fournir `response` pour piloter
    le comportement dans des tests qui doivent exercer d'autres chemins du
    pipeline de qualification (confiance faible, JSON invalide, exclusion,
    échec du LLM) : un dict (sérialisé en JSON), une chaîne JSON brute, ou
    une exception (instance ou classe) à lever."""

    def __init__(
        self,
        response: dict | str | Exception | type[Exception] | None = None,
    ):
        self._response = DEFAULT_RESPONSE if response is None else response

    def analyze(self, text: str) -> str:
        if isinstance(self._response, Exception):
            raise self._response

        if isinstance(self._response, type) and issubclass(
            self._response, Exception
        ):
            raise self._response("FakeLLM configured to raise.")

        if isinstance(self._response, str):
            return self._response

        return json.dumps(self._response)
