class QualificationError(Exception):
    """Exception de base du module qualification."""

class InvalidQualificationError(QualificationError):
    """Résultat de qualification invalide."""


class LLMError(QualificationError):
    """Erreur lors de l'appel au modèle de langage."""