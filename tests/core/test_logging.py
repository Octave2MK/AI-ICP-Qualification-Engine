import logging

from app.core.logging import SecretRedactionFilter, get_logger


def test_logger_creation():

    logger = get_logger(
        "test"
    )

    assert logger.name == "test"


def test_secret_redaction_filter_redacts_configured_secret():
    filt = SecretRedactionFilter(secrets=["super-secret-key"])
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="calling API with key=%s",
        args=("super-secret-key",),
        exc_info=None,
    )

    filt.filter(record)

    assert "super-secret-key" not in record.getMessage()
    assert "***REDACTED***" in record.getMessage()


def test_secret_redaction_filter_is_noop_when_no_secrets_configured():
    filt = SecretRedactionFilter(secrets=[])
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )

    filt.filter(record)

    assert record.getMessage() == "hello world"