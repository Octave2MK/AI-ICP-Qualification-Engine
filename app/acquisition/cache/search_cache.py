import time
from typing import Any


class SearchCache:
    """
    Cache mémoire simple pour les recherches.
    """
    def __init__(
        self,
        ttl: int = 3600,
    ):
        self.ttl = ttl
        self._cache: dict[str, tuple[Any, float]] = {}


    def get(
        self,
        key: str,
    ):
        item = self._cache.get(key)

        if not item:
            return None

        value, timestamp = item

        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None
        return value

    def set(
        self,
        key: str,
        value,
    ):
        self._cache[key] = (
            value,
            time.time(),
        )