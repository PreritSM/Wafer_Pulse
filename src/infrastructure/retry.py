import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def with_exponential_backoff(
    fn: Callable[..., T],
    *args: Any,
    retries: int = 3,
    base_delay_seconds: float = 0.5,
    **kwargs: Any,
) -> T:
    """Run a callable with bounded exponential backoff retry behavior."""
    attempts = 0
    while True:
        try:
            return fn(*args, **kwargs)
        except Exception:
            attempts += 1
            if attempts >= retries:
                raise
            sleep_seconds = base_delay_seconds * (2 ** (attempts - 1))
            time.sleep(sleep_seconds)
