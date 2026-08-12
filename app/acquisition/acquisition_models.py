from dataclasses import dataclass, field


@dataclass
class ICP:
    """
    Représente un profil cible (Ideal Customer Profile).
    """
    job_titles: list[str]
    countries: list[str]
    languages: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    required_keywords: list[str] = field(default_factory=list)
    forbidden_keywords: list[str] = field(default_factory=list)

@dataclass
class SearchQuery:
    """
    Une requête générée pour un moteur de recherche.
    """
    text: str

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""

@dataclass
class ProspectCandidate:

    url: str

    title: str = ""

    snippet: str = ""