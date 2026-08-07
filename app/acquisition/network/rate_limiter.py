import time


class RateLimiter:
    """
    Limite le nombre d'appels dans le temps.
    """
    def __init__(
        self,
        min_interval: float = 1.0,
    ):
        self.min_interval = min_interval
        self.last_call = 0.0

    def wait(self):
        """
        Attend si nécessaire avant le prochain appel.
        """

        elapsed = time.time() - self.last_call

        if elapsed < self.min_interval:
            time.sleep(
                self.min_interval - elapsed
            )
        self.last_call = time.time()