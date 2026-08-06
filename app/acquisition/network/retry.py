import time
from functools import wraps


def retry(
    attempts: int,
    delay: float = 1,
    exceptions=(Exception,),
):
    """
    Réessaie une fonction en cas d'erreur.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc

                    if attempt < attempts - 1:
                        time.sleep(
                            delay * (attempt + 1)
                        )

            raise last_exception

        return wrapper

    return decorator