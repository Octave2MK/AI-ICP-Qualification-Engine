from unittest.mock import patch, Mock

from app.acquisition.searxng_provider import (
    SearXNGProvider,
)

from app.acquisition.acquisition_models import (
    SearchQuery,
)


@patch(
    "app.acquisition.searxng_provider.httpx.get"
)
def test_search_logs_results(
    mock_get,
    caplog,
):

    caplog.set_level("INFO")


    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {
        "results": []
    }

    mock_get.return_value = response


    provider = SearXNGProvider()


    provider.search(
        SearchQuery(
            text="Business Coach"
        )
    )


    assert (
        "SearXNG returned 0 results"
        in caplog.text
    )