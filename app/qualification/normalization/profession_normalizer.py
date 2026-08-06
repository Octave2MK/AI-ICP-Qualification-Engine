class ProfessionNormalizer:
    _MAPPINGS = {
        "coach business": "Business Coach",
        "business coach": "Business Coach",
        "coach de dirigeants": "Business Coach",
        "coach d'entrepreneurs": "Business Coach",
        "coach entrepreneur": "Business Coach",
        "coach en développement d'entreprise": "Business Coach",
        "consultant en croissance": "Business Coach",
        "consultant croissance pme": "Business Coach",
        "mentor business": "Business Coach",
    }

    @classmethod
    def normalize(cls, profession: str) -> str:
        if not profession:
            return ""

        normalized = profession.strip().lower()

        return cls._MAPPINGS.get(
            normalized,
            profession.strip(),
        )