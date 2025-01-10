import logging
from unittest.mock import Mock

import fakeredis
import pytest

from civil_registry.core.middleware.apitrack import APICallTrackingMiddleware
from civil_registry.core.middleware.requestid import RequestIDMiddleware
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
def api_call_data():
    return {
        "path": "/test-path",
        "request_id": "test_request_id",
        "method": "GET",
        "user_id": 1,
        "user_agent": "test-agent",
        "status_code": 200,
        "response_data": {"id_number": "12345", "detail": "test detail"},
    }


@pytest.fixture
def get_response():
    return Mock()


@pytest.fixture
def apitrack_middleware(get_response):
    return APICallTrackingMiddleware(get_response)


@pytest.fixture
def requestid_middleware(get_response):
    return RequestIDMiddleware(get_response)


@pytest.fixture
def requestid_request():
    req = Mock()
    req.headers = {}
    req.method = "GET"
    req.path = "/test-path"
    return req


@pytest.fixture
def response():
    res = Mock()
    res.status_code = 200
    return res


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
