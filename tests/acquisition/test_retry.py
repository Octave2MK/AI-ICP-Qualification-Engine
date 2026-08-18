from unittest.mock import patch

import pytest

from app.acquisition.network.retry import retry


def test_retry_succeeds_after_failure():

    calls = {
        "count": 0
    }

    @retry(attempts=3)
    def unstable_function():

        calls["count"] += 1

        if calls["count"] < 3:
            raise Exception()

        return "success"


    result = unstable_function()

    assert result == "success"
    assert calls["count"] == 3


def test_retry_raises_original_exception_after_exhausting_attempts():
    calls = {"count": 0}

    class BoomError(Exception):
        pass

    @retry(attempts=3, delay=0)
    def always_failing_function():
        calls["count"] += 1
        raise BoomError(f"attempt {calls['count']}")

    with pytest.raises(BoomError, match="attempt 3"):
        always_failing_function()

    assert calls["count"] == 3


@patch("app.acquisition.network.retry.time.sleep")
def test_retry_applies_increasing_backoff_between_attempts(mock_sleep):
    calls = {"count": 0}

    @retry(attempts=3, delay=2)
    def unstable_function():
        calls["count"] += 1
        if calls["count"] < 3:
            raise Exception()
        return "success"

    unstable_function()

    assert mock_sleep.call_args_list == [
        ((2,),),
        ((4,),),
    ]


def test_retry_does_not_catch_unlisted_exception_types():
    @retry(attempts=3, delay=0, exceptions=(ValueError,))
    def raises_type_error():
        raise TypeError("not retried")

    with pytest.raises(TypeError, match="not retried"):
        raises_type_error()