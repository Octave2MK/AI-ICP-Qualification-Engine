from dataclasses import dataclass, field
import re

from app.acquisition.acquisition_models import ICP, ProspectCandidate


@dataclass
class RelevanceResult:
    """
    Résultat de l'évaluation de pertinence d'un candidat.
    """

    score: int
    passed: bool
    matched_titles: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    matched_forbidden_keywords: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class RelevanceFilter:
    """
    Évalue la pertinence d'un prospect à partir des données
    disponibles dans les résultats du moteur de recherche.

    Le filtre intervient avant l'enrichissement afin d'éviter
    de scraper et qualifier des profils manifestement hors ICP.
    """

    TITLE_EXACT_SCORE = 50
    TITLE_PARTIAL_SCORE = 30
    KEYWORD_TITLE_SCORE = 15
    KEYWORD_SNIPPET_SCORE = 10
    COUNTRY_SCORE = 10

    FORBIDDEN_PENALTY = 100

    DEFAULT_THRESHOLD = 50

    def __init__(self, threshold: int = DEFAULT_THRESHOLD):
        self.threshold = threshold

    def evaluate(
        self,
        candidate: ProspectCandidate,
        icp: ICP,
    ) -> RelevanceResult:
        """
        Évalue un candidat et retourne son score de pertinence.
        """

        title = self._normalize(candidate.title or "")
        snippet = self._normalize(candidate.snippet or "")
        searchable_text = f"{title} {snippet}".strip()


        score = 0

        matched_titles: list[str] = []
        matched_keywords: list[str] = []
        matched_forbidden_keywords: list[str] = []
        reasons: list[str] = []

        # ---------------------------------------------------------
        # 1. Termes interdits
        # ---------------------------------------------------------

        for forbidden in icp.forbidden_keywords:
            normalized_forbidden = self._normalize(forbidden)

            if normalized_forbidden and self._contains(
                searchable_text,
                normalized_forbidden,
            ):
                matched_forbidden_keywords.append(forbidden)

        if matched_forbidden_keywords:
            score -= self.FORBIDDEN_PENALTY

            reasons.append(
                "Forbidden keyword detected: "
                + ", ".join(matched_forbidden_keywords)
            )

        # ---------------------------------------------------------
        # 2. Métier / titre professionnel
        # ---------------------------------------------------------

        for job_title in icp.job_titles:
            normalized_title = self._normalize(job_title)

            if not normalized_title:
                continue

            if self._contains(title, normalized_title):
                score += self.TITLE_EXACT_SCORE
                matched_titles.append(job_title)

                reasons.append(
                    f"Job title detected in title: {job_title}"
                )

            elif self._contains(searchable_text, normalized_title):
                score += self.TITLE_PARTIAL_SCORE
                matched_titles.append(job_title)

                reasons.append(
                    f"Job title detected in search result: {job_title}"
                )

        # ---------------------------------------------------------
        # 3. Keywords
        # ---------------------------------------------------------

        for keyword in icp.keywords:
            normalized_keyword = self._normalize(keyword)

            if not normalized_keyword:
                continue

            if self._contains(title, normalized_keyword):
                score += self.KEYWORD_TITLE_SCORE
                matched_keywords.append(keyword)

                reasons.append(
                    f"Keyword detected in title: {keyword}"
                )

            elif self._contains(snippet, normalized_keyword):
                score += self.KEYWORD_SNIPPET_SCORE
                matched_keywords.append(keyword)

                reasons.append(
                    f"Keyword detected in snippet: {keyword}"
                )

        # ---------------------------------------------------------
        # 4. Pays
        # ---------------------------------------------------------

        for country in icp.countries:
            normalized_country = self._normalize(country)

            if not normalized_country:
                continue

            if self._contains(searchable_text, normalized_country):
                score += self.COUNTRY_SCORE

                reasons.append(
                    f"Country detected: {country}"
                )

                break

        # ---------------------------------------------------------
        # 5. Décision finale
        # ---------------------------------------------------------

        passed = (
            score >= self.threshold
            and not matched_forbidden_keywords
        )

        if passed:
            reasons.append("Candidate passed relevance threshold.")
        else:
            reasons.append("Candidate rejected by relevance filter.")

        return RelevanceResult(
            score=score,
            passed=passed,
            matched_titles=matched_titles,
            matched_keywords=matched_keywords,
            matched_forbidden_keywords=matched_forbidden_keywords,
            reasons=reasons,
        )

    def is_relevant(
        self,
        candidate: ProspectCandidate,
        icp: ICP,
    ) -> bool:
        """
        Retourne uniquement la décision de filtrage.
        """

        return self.evaluate(candidate, icp).passed

    @staticmethod
    def _normalize(value: str) -> str:
        """
        Normalise un texte pour rendre les comparaisons
        insensibles à la casse et aux espaces multiples.
        """

        if not value:
            return ""

        value = value.lower().strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value

    @staticmethod
    def _contains(
        text: str,
        term: str,
    ) -> bool:
        """
        Recherche un terme dans un texte.

        La recherche accepte :
        - le terme exact ;
        - une variante plurielle simple avec 's'.

        Exemples :
            entrepreneur -> entrepreneur
            entrepreneur -> entrepreneurs
            coach -> coach
            coach -> coaches
        """

        if not text or not term:
            return False

        # Recherche exacte
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

        if re.search(pattern, text):
            return True

        # Tolérance du pluriel simple
        if not term.endswith("s"):
            plural_pattern = (
                r"(?<!\w)"
                + re.escape(term)
                + r"s"
                + r"(?!\w)"
            )

            if re.search(plural_pattern, text):
                return True

        return False