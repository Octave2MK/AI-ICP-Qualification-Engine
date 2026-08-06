class ICPPreFilter:
    """
    Filtrage rapide avant appel LLM.
    Évite les appels Gemini inutiles.
    """

    KEYWORDS = [
        "coach",
        "consultant",
        "consulting",
        "expert",
        "formateur",
        "formation",
        "conseil",
        "stratégie",
        "business",
    ]


    @classmethod
    def match(cls, profile) -> bool:

        text = " ".join(
            [
                profile.name or "",
                profile.headline or "",
                profile.about or "",
            ]
        ).lower()


        for keyword in cls.KEYWORDS:

            if keyword in text:
                return True


        return False