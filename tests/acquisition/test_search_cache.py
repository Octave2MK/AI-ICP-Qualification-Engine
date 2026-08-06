from app.acquisition.cache.search_cache import (
    SearchCache,
)


def test_cache_returns_saved_value():

    cache = SearchCache()


    cache.set(
        "coach france",
        ["result"],
    )


    result = cache.get(
        "coach france"
    )


    assert result == [
        "result"
    ]



def test_cache_returns_none_when_missing():

    cache = SearchCache()


    result = cache.get(
        "unknown"
    )


    assert result is None