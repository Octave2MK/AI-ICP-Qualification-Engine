from unittest.mock import Mock, patch
import pytest

from app.acquisition.acquisition_models import SearchQuery
from app.acquisition.searxng_provider import SearXNGProvider
import httpx

from app.acquisition.exceptions import SearXNGError
from unittest.mock import patch


@patch(
    "app.acquisition.network.rate_limiter.time.sleep"
)
@patch("app.acquisition.searxng_provider.httpx.get")
def test_search_returns_search_results(    
    mock_get,
    mock_sleep,
):
    mock_response = Mock()

    mock_response.json.return_value = {
        "results": [
            {
                "title": "John Doe",
                "url": "https://www.linkedin.com/in/john-doe",
                "content": "Business Coach",
            },
            {
                "title": "Jane Smith",
                "url": "https://www.linkedin.com/in/jane-smith",
                "content": "Sales Coach",
            },
        ]
    }

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    provider = SearXNGProvider()

    results = provider.search(
        SearchQuery(
            text="Business Coach France"
        )
    )

    assert len(results) == 2

    assert results[0].title == "John Doe"
    assert results[0].url == "https://www.linkedin.com/in/john-doe"
    assert results[0].snippet == "Business Coach"


@patch(
    "app.acquisition.network.rate_limiter.time.sleep"
)
@patch("app.acquisition.searxng_provider.httpx.get")
def test_search_returns_search_results(
    mock_get,
    mock_sleep,
):
    mock_response = Mock()

    mock_response.json.return_value = {
        "results": []
    }

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    provider = SearXNGProvider()

    results = provider.search(
        SearchQuery(
            text="Unknown ICP"
        )
    )

    assert results == []


@patch(
    "app.acquisition.network.rate_limiter.time.sleep"
)
@patch("app.acquisition.searxng_provider.httpx.get")
def test_timeout_raises_searxng_error(
    mock_get,
    mock_sleep,
):
    mock_get.side_effect = httpx.TimeoutException(
        "timeout"
    )

    provider = SearXNGProvider()

    with pytest.raises(SearXNGError):
        provider.search(
            SearchQuery(
                text="Business Coach"
            )
        )


@patch(
    "app.acquisition.network.rate_limiter.time.sleep"
)
@patch("app.acquisition.searxng_provider.httpx.get")
def test_retry_after_http_failure(    
    mock_get,
    mock_sleep,
):

    failed_response = Mock()

    failed_response.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "500",
            request=Mock(),
            response=Mock(),
        )
    )


    success_response = Mock()

    success_response.raise_for_status.return_value = None

    success_response.json.return_value = {
        "results": []
    }


    mock_get.side_effect = [
        failed_response,
        success_response,
    ]


    provider = SearXNGProvider()

    results = provider.search(
        SearchQuery(
            text="Coach"
        )
    )


    assert results == []
    assert mock_get.call_count == 2