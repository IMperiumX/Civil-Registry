from unittest.mock import Mock
from unittest.mock import patch

import pytest
from django.http import HttpRequest
from django.http import HttpResponse

from civil_registry.core.middleware.apitrack import APICallTrackingMiddleware


@pytest.fixture
def get_response():
    return Mock()


@pytest.fixture
def middleware(get_response):
    return APICallTrackingMiddleware(get_response)


def test_process_view_trackable(middleware):
    request = HttpRequest()
    view_func = Mock()
    view_func.view_class = Mock(track_endpoint=True)
    middleware.process_view(request, view_func, [], {})
    assert hasattr(request, "is_trackable")


def test_process_view_not_trackable(middleware):
    request = HttpRequest()
    view_func = Mock()
    view_func.view_class = Mock(track_endpoint=False)
    middleware.process_view(request, view_func, [], {})
    assert not hasattr(request, "is_trackable")


def test_process_view_no_view_class(middleware):
    request = HttpRequest()
    view_func = Mock()
    del view_func.view_class  # must be deleted to simulate the absence of view_class as the Mock object has it by default
    middleware.process_view(request, view_func, [], {})
    is_trackable = getattr(request, "is_trackable", False)
    assert not is_trackable


@patch("civil_registry.core.middleware.apitrack.create_api_call_record.delay")
def test_process_response_trackable(mock_create_api_call_record, middleware):
    request = HttpRequest()
    request.is_trackable = True
    request.request_id = "test_request_id"
    request.method = "GET"
    request.path = "/test-path"
    request.user = Mock(is_authenticated=True, id=1)
    request.META = {"HTTP_USER_AGENT": "test-agent"}
    response = HttpResponse()
    response.status_code = 200
    response.data = {"id_number": "12345", "detail": "test detail"}

    middleware.process_response(request, response)
    assert mock_create_api_call_record.called


def test_process_response_not_trackable(middleware):
    view_func = Mock()
    request = HttpRequest()
    response = HttpResponse()

    view_func.view_class = Mock(track_endpoint=False)
    request.request_id = "test_request_id"  # for logging
    middleware.process_view(request, None, [], {})
    response = middleware.process_response(request, response)
    assert response.status_code == 200  # noqa: PLR2004


def test_get_client_ip_forwarded(middleware):
    request = HttpRequest()
    request.META = {"HTTP_X_FORWARDED_FOR": "192.168.0.1, 192.168.0.2"}
    ip = middleware._get_client_ip(request)  # noqa: SLF001
    assert ip == "192.168.0.1"


def test_get_client_ip_remote_addr(middleware):
    request = HttpRequest()
    request.META = {"REMOTE_ADDR": "192.168.0.1"}
    ip = middleware._get_client_ip(request)  # noqa: SLF001
    assert ip == "192.168.0.1"


def test_get_client_ip_no_forwarded(middleware):
    request = HttpRequest()
    request.META = {}
    ip = middleware._get_client_ip(request)  # noqa: SLF001
    assert ip is None


def test_failed_open(middleware):
    request = HttpRequest()
    response = HttpResponse()
    request.is_trackable = True
    request.request_id = "test_request_id"
    request.method = "GET"
    request.path = "/test-path"
    request.user = Mock(is_authenticated=True, id=1)
    request.META = {"HTTP_USER_AGENT": "test-agent"}
    response = middleware.process_response(request, response)
    assert response.status_code == 200  # noqa: PLR2004
