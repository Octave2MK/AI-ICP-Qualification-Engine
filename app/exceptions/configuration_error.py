class ConfigurationError(Exception):
    """Levée lorsque la configuration de l'application est invalide ou
    incomplète pour l'opération demandée (ex. clé API manquante)."""
