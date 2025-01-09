from dataclasses import dataclass
from enum import Enum


class RateLimitCategory(str, Enum):
    IP = "ip"
    USER = "user"


@dataclass
class RateLimit:
    """Dataclass for defining a rate limit

    Attributes:
        limit (int): Max number of hits allowed within the window
        window (int): Period of time in seconds that the rate limit applies for

    """

    limit: int
    window: int


class RateLimitType(Enum):
    NOT_LIMITED = "not_limited"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitMeta:
    """
    Rate Limit response metadata

    Attributes:
        is_limited (bool): request is rate limited
        current (int): number of requests done in the current window
        remaining (int): number of requests left in the current window
        limit (int): max number of requests per window
        window (int): window size in seconds
        reset_time (int): UTC Epoch time in seconds when the current window expires
    """

    rate_limit_type: RateLimitType
    current: int
    remaining: int
    limit: int
    window: int
    group: str
    reset_time: int
