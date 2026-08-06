from dataclasses import dataclass, field


@dataclass(slots=True)
class QualificationResult:
    profession: str
    sector: str
    target_market: str

    offer_detected: bool

    authority_signals: list[str] = field(default_factory=list)
    content_signals: list[str] = field(default_factory=list)
    commercial_signals: list[str] = field(default_factory=list)

    icp_match: bool = False

    confidence: float = 0.0

    evidence: list[str] = field(default_factory=list)

    exclusion_reason: str | None = None