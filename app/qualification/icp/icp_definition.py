from dataclasses import dataclass, field
import hashlib
import json


@dataclass(slots=True)
class ICPDefinition:
    professions: list[str] = field(default_factory=list)

    sectors: list[str] = field(default_factory=list)

    target_markets: list[str] = field(default_factory=list)

    required_keywords: list[str] = field(default_factory=list)

    forbidden_keywords: list[str] = field(default_factory=list)

    minimum_confidence: float = 0.70

    def fingerprint(self) -> str:
        """Return a stable identifier for this exact ICP definition."""
        payload = {
            "professions": sorted(self.professions),
            "sectors": sorted(self.sectors),
            "target_markets": sorted(self.target_markets),
            "required_keywords": sorted(self.required_keywords),
            "forbidden_keywords": sorted(self.forbidden_keywords),
            "minimum_confidence": self.minimum_confidence,
        }

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()
