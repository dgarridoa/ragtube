import signal
from functools import wraps


def timeout_handler(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(
                f"Function '{func.__name__}' timed out after {seconds} seconds"
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the signal handler and a timeout alarm
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm
                signal.alarm(0)
            return result

        return wrapper

    return decorator
