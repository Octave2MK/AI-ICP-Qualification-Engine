class SectorNormalizer:

    _MAPPINGS = {
        "consulting": "Consulting",
        "consultancy": "Consulting",
        "business consulting": "Consulting",
        "coaching": "Consulting",
    }

    @classmethod
    def normalize(cls, sector: str) -> str:
        if not sector:
            return ""

        normalized = sector.strip().lower()

        return cls._MAPPINGS.get(
            normalized,
            sector.strip(),
        )