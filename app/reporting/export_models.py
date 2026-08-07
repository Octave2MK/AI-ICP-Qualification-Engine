from dataclasses import dataclass, field


@dataclass
class ProspectExportData:
    linkedin_url: str
    name: str
    headline: str
    profession: str
    sector: str
    target_market: str
    offer_detected: bool
    icp_match: bool
    confidence: float

    authority_signals: list[str] = field(
        default_factory=list
    )

    content_signals: list[str] = field(
        default_factory=list
    )
    
    commercial_signals: list[str] = field(
        default_factory=list
    )

    evidence: list[str] = field(
        default_factory=list
    )

    exclusion_reason: str | None = None