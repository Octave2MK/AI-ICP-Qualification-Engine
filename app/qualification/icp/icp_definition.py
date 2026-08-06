from dataclasses import dataclass, field


@dataclass(slots=True)
class ICPDefinition:
    professions: list[str] = field(default_factory=list)

    sectors: list[str] = field(default_factory=list)

    target_markets: list[str] = field(default_factory=list)

    required_keywords: list[str] = field(default_factory=list)

    forbidden_keywords: list[str] = field(default_factory=list)

    minimum_confidence: float = 0.70