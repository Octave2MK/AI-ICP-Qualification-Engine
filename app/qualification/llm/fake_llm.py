import json

from app.qualification.interfaces import BaseLLM


class FakeLLM(BaseLLM):
    def analyze(self, text: str) -> str:
        return json.dumps(
            {
                "profession": "Business Coach",
                "sector": "Consulting",
                "target_market": "B2B",
                "offer_detected": True,
                "authority_signals": [
                    "Speaker"
                ],
                "content_signals": [
                    "Publishes on LinkedIn"
                ],
                "commercial_signals": [
                    "Call booking link"
                ],
                "icp_match": True,
                "confidence": 0.95,
                "evidence": [
                    "Headline mentions business coaching"
                ],
                "exclusion_reason": None,
            }
        )