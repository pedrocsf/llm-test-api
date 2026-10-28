from collections.abc import Callable

ProgressListener = Callable[[int, int], None]
CancellationCheck = Callable[[], bool]


def ignore_progress(completed: int, total: int) -> None:
    return None


def never_cancelled() -> bool:
    return False
