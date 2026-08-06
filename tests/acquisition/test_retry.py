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