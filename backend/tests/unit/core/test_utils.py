import time

import pytest

from ragtube.core.utils import timeout_handler


def test_timeout():
    @timeout_handler(1)
    def throw_timeout_error():
        time.sleep(2)

    @timeout_handler(2)
    def not_throw_timeout_error():
        time.sleep(1)

    with pytest.raises(TimeoutError):
        throw_timeout_error()
    not_throw_timeout_error()
