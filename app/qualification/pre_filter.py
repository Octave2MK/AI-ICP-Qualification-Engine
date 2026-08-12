import re

from app.qualification.icp.icp_definition import ICPDefinition


class ICPPreFilter:
    """
    Filtrage rapide avant appel LLM.
    Évite les appels Gemini inutiles en vérifiant les critères
    réellement définis par l'ICP courant.
    """

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        term = term.strip().lower()
        if not term:
            return False

        pattern = r"\b" + re.escape(term) + r"(?:s|es)?\b"
        return re.search(pattern, text) is not None

    @classmethod
    def match(
        cls,
        profile,
        icp: ICPDefinition,
    ) -> bool:
        text = " ".join(
            [
                profile.name or "",
                profile.headline or "",
                profile.about or "",
                profile.clean_text or "",
            ]
        ).lower()

        professions = icp.professions or []
        required_keywords = icp.required_keywords or []

        if not professions and not required_keywords:
            return False

        profession_match = any(
            cls._contains_term(text, profession)
            for profession in professions
        )

        required_match = all(
            cls._contains_term(text, keyword)
            for keyword in required_keywords
        )

        if professions and required_keywords:
            return profession_match and required_match

        if professions:
            return profession_match

        return required_match
