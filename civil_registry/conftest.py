import logging

import fakeredis
import pytest

from civil_registry.core.ratelimit import RedisRateLimiter


def pytest_configure():
    # disable loggin while running tests
    # remove middleware from settings
    logging.disable(logging.CRITICAL)

    # remove middleware from settings
    from django.conf import settings

    settings.MIDDLEWARE = [
        middleware
        for middleware in settings.MIDDLEWARE
        if "RequestIDMiddleware" not in middleware
    ]


@pytest.fixture
def fake_redis_server():
    """
    Fixture to provide a fakeredis server instance.
    """
    server = fakeredis.FakeServer()
    yield server
    server.connected = False  # Properly disconnect after use to release open sockets


@pytest.fixture
def redis_client(fake_redis_server):
    """
    Fixture to provide a Redis client connected to the fakeredis server.
    """
    client = fakeredis.FakeStrictRedis(server=fake_redis_server)
    yield client
    client.flushall()  # Clear data after each test


@pytest.fixture
def rate_limiter(redis_client):
    rate_limiter = RedisRateLimiter()
    rate_limiter.client = redis_client
    return rate_limiter
