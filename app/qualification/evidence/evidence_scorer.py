class EvidenceScorer:
    @staticmethod
    def score(evidence: list[str]) -> float:

        if not evidence:
            return 0.0

        score = 0.0

        for item in evidence:
            text = item.lower()
            if "headline" in text:
                score += 0.4
            elif "about" in text:
                score += 0.3
            elif "target" in text:
                score += 0.2
            else:
                score += 0.1
        return min(score, 1.0)