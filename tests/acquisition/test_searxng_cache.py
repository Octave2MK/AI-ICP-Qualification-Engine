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
def test_second_search_uses_cache(
    mock_get,
):

    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {
        "results": [
            {
                "title": "John Doe",
                "url": "https://linkedin.com/in/john",
                "content": "Coach",
            }
        ]
    }


    mock_get.return_value = response


    provider = SearXNGProvider()


    query = SearchQuery(
        text="Business Coach"
    )


    first = provider.search(query)

    second = provider.search(query)


    assert first == second


    assert (
        mock_get.call_count == 1
    )