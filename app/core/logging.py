import logging
import sys

from app.core.settings import settings


class SecretRedactionFilter(logging.Filter):
    """Rédige les secrets configurés (clés API) des messages de log, en
    défense en profondeur même si aucun appel actuel ne les logue."""

    def __init__(self, secrets: list[str] | None = None):
        super().__init__()
        if secrets is None:
            secrets = [settings.GEMINI_API_KEY, settings.OPENAI_API_KEY]
        self._secrets = [value for value in secrets if value]

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._secrets:
            return True

        message = record.getMessage()
        redacted = message
        for secret in self._secrets:
            redacted = redacted.replace(secret, "***REDACTED***")

        if redacted != message:
            record.msg = redacted
            record.args = ()

        return True


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(SecretRedactionFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]


def get_logger(name: str):
    return logging.getLogger(name)
