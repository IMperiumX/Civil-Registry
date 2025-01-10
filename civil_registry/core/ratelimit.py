from __future__ import annotations

import logging
from time import time
from typing import Any

from django.conf import settings
from redis import StrictRedis
from redis.exceptions import RedisError

from civil_registry.core.exceptions import InvalidConfigurationError
from civil_registry.core.utils import md5_text

logger = logging.getLogger(__name__)


class RateLimiter:
    def is_limited(
        self,
        key: str,
        limit: int,
        window: int | None = None,
    ) -> bool:
        is_limited, _, _ = self.is_limited_with_value(key, limit, window=window)
        return is_limited

    def current_value(
        self,
        key: str,
        window: int | None = None,
    ) -> int:
        return 0

    def is_limited_with_value(
        self,
        key: str,
        limit: int,
        window: int | None = None,
    ) -> tuple[bool, int, int]:
        return False, 0, 0

    def validate(self) -> None:
        raise NotImplementedError

    def reset(
        self,
        key: str,
        window: int | None = None,
    ) -> None:
        return


def _time_bucket(request_time: float, window: int) -> int:
    """Bucket number lookup for given UTC time since epoch"""
    return int(request_time / window)


def _bucket_start_time(bucket_number: int, window: int) -> int:
    """Determine bucket start time in seconds from epoch in UTC"""
    return bucket_number * window


class RedisRateLimiter(RateLimiter):
    """
    RateLimiter implementation using Redis as the backend storage for rate limiting.
    Suitable for distributed rate limiting across multiple servers.
    """

    def __init__(self, window: int = 60, **options: Any) -> None:
        self.client: StrictRedis[str] = StrictRedis.from_url(settings.REDIS_URL)
        self.window = window

    def _construct_redis_key(
        self,
        key: str,
        window: int | None = None,
        request_time: float | None = None,
    ) -> str:
        """
        Construct a rate limit key using the args given. Key will have a format of:
        "rl:<key_hex>:<time_bucket>"
        where the time bucket is calculated by integer dividing the current time by the window
        """

        if window is None or window == 0:
            window = self.window

        if request_time is None:
            request_time = time()

        key_hex = md5_text(key).hexdigest()
        time_bucket = _time_bucket(request_time, window)

        return f"rl:{key_hex}:{time_bucket}"

    def validate(self) -> None:
        try:
            self.client.ping()
            self.client.connection_pool.disconnect()
        except Exception as e:
            raise InvalidConfigurationError(str(e)) from e

    def current_value(
        self,
        key: str,
        window: int | None = None,
    ) -> int:
        """
        Get the current value stored in redis for the rate limit with key "key" and said window
        """
        redis_key = self._construct_redis_key(key, window=window)

        try:
            current_count = self.client.get(redis_key)
        except RedisError:
            # Don't report any existing hits when there is a redis error.
            # Log what happened and move on
            logger.exception("Failed to retrieve current value from redis")
            return 0

        if current_count is None:
            # Key hasn't been created yet, therefore no hits done so far
            return 0
        return int(current_count)

    def is_limited_with_value(
        self,
        key: str,
        limit: int,
        window: int | None = None,
    ) -> tuple[bool, int, int]:
        """
        Does a rate limit check as well as returning the new rate limit value and when the next
        rate limit window will start.

        Note that the counter is incremented when the check is done.
        """
        request_time = time()
        if window is None or window == 0:
            window = self.window
        redis_key = self._construct_redis_key(
            key,
            window=window,
            request_time=request_time,
        )

        expiration = window - int(request_time % window)
        # Reset Time = next time bucket's start time
        reset_time = _bucket_start_time(_time_bucket(request_time, window) + 1, window)
        try:
            pipe = self.client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, expiration)
            pipeline_result = pipe.execute()

            # Handle potential None result (unlikely with incr and expire)
            if None in pipeline_result:
                logger.warning("Redis pipeline returned None for one of the commands.")
                return False, 0, reset_time

            result = pipeline_result[0]
        except RedisError:
            # We don't want rate limited endpoints to fail when ratelimits
            # can't be updated. We do want to know when that happens.
            logger.exception("Failed to retrieve current value from redis")
            return False, 0, reset_time

        return result > limit, result, reset_time

    def reset(self, key: str, window: int | None = None) -> None:
        redis_key = self._construct_redis_key(key, window=window)
        self.client.delete(redis_key)
