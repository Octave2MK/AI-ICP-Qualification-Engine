from unittest.mock import patch

from app.acquisition.network.rate_limiter import RateLimiter


@patch("app.acquisition.network.rate_limiter.time.sleep")
@patch("app.acquisition.network.rate_limiter.time.time")
def test_rate_limiter_waits_when_needed(
    mock_time,
    mock_sleep,
):

    mock_time.side_effect = [
        10,      # premier appel time.time()
        10,      # mise à jour last_call
        10.5,    # deuxième appel time.time()
        10.5,    # mise à jour last_call
    ]

    limiter = RateLimiter(
        min_interval=1
    )

    limiter.wait()
    limiter.wait()

    mock_sleep.assert_called_once_with(0.5)


@patch("app.acquisition.network.rate_limiter.time.sleep")
@patch("app.acquisition.network.rate_limiter.time.time")
def test_rate_limiter_does_not_wait_when_interval_already_elapsed(
    mock_time,
    mock_sleep,
):
    mock_time.side_effect = [
        10,    # premier appel time.time()
        10,    # mise à jour last_call
        20,    # deuxième appel time.time(), largement au-delà de min_interval
        20,    # mise à jour last_call
    ]

    limiter = RateLimiter(min_interval=1)

    limiter.wait()
    limiter.wait()

    mock_sleep.assert_not_called()