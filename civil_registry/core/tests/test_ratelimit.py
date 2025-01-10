from time import time

from civil_registry.core.utils import freeze_time


def test_simple_key(rate_limiter):
    with freeze_time("2000-01-01"):
        assert not rate_limiter.is_limited("foo", 1)
        assert rate_limiter.is_limited("foo", 1)


def test_correct_current_value(rate_limiter):
    """Ensure that current_value get the correct value after the counter in incremented"""

    with freeze_time("2000-01-01"):
        for _ in range(10):
            rate_limiter.is_limited("foo", 100)

        assert rate_limiter.current_value("foo") == 10
        rate_limiter.is_limited("foo", 100)
        assert rate_limiter.current_value("foo") == 11


def test_current_value_new_key(rate_limiter):
    """current_value should return 0 for a new key"""

    assert rate_limiter.current_value("new") == 0


def test_current_value_expire(rate_limiter):
    """Ensure that the count resets when the window expires"""
    with freeze_time("2000-01-01") as frozen_time:
        for _ in range(10):
            rate_limiter.is_limited("foo", 1, window=10)
        assert rate_limiter.current_value("foo", window=10) == 10

        frozen_time.shift(10.1)
        assert rate_limiter.current_value("foo", window=10) == 0


def test_is_limited_with_value(rate_limiter):
    with freeze_time("2000-01-01") as frozen_time:
        expected_reset_time = int(time() + 5)

        limited, value, reset_time = rate_limiter.is_limited_with_value(
            "foo",
            1,
            window=5,
        )
        assert not limited
        assert value == 1
        assert reset_time == expected_reset_time

        limited, value, reset_time = rate_limiter.is_limited_with_value(
            "foo",
            1,
            window=5,
        )
        assert limited
        assert value == 2
        assert reset_time == expected_reset_time

        frozen_time.shift(5.1)
        limited, value, reset_time = rate_limiter.is_limited_with_value(
            "foo",
            1,
            window=5,
        )
        assert not limited
        assert value == 1
        assert reset_time == expected_reset_time + 5


def test_reset(rate_limiter):
    with freeze_time("2000-01-01"):
        assert not rate_limiter.is_limited("foo", 1)
        assert rate_limiter.is_limited("foo", 1)
        rate_limiter.reset("foo")
        assert not rate_limiter.is_limited("foo", 1)
