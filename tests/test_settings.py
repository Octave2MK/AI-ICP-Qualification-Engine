from app.core.settings import settings


def test_request_timeout():
    assert settings.REQUEST_TIMEOUT > 0


def test_user_agent_not_empty():
    assert settings.USER_AGENT != ""