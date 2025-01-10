from unittest.mock import Mock
from unittest.mock import patch

from django.http import HttpRequest
from django.http import HttpResponse


def test_process_view_trackable(apitrack_middleware):
    request = HttpRequest()
    view_func = Mock()
    view_func.view_class = Mock(track_endpoint=True)
    apitrack_middleware.process_view(request, view_func, [], {})
    assert hasattr(request, "is_trackable")


def test_process_view_not_trackable(apitrack_middleware):
    request = HttpRequest()
    view_func = Mock()
    view_func.view_class = Mock(track_endpoint=False)
    apitrack_middleware.process_view(request, view_func, [], {})
    assert not hasattr(request, "is_trackable")


def test_process_view_no_view_class(apitrack_middleware):
    request = HttpRequest()
    view_func = Mock()
    del view_func.view_class  # must be deleted to simulate the absence of view_class as the Mock object has it by default
    apitrack_middleware.process_view(request, view_func, [], {})
    is_trackable = getattr(request, "is_trackable", False)
    assert not is_trackable


@patch("civil_registry.core.middleware.apitrack.create_api_call_record.delay")
def test_process_response_trackable(mock_create_api_call_record, apitrack_middleware):
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

    apitrack_middleware.process_response(request, response)
    assert mock_create_api_call_record.called


def test_process_response_not_trackable(apitrack_middleware):
    view_func = Mock()
    request = HttpRequest()
    response = HttpResponse()

    view_func.view_class = Mock(track_endpoint=False)
    request.request_id = "test_request_id"  # for logging
    apitrack_middleware.process_view(request, None, [], {})
    response = apitrack_middleware.process_response(request, response)
    assert response.status_code == 200  # noqa: PLR2004


def test_get_client_ip_forwarded(apitrack_middleware):
    request = HttpRequest()
    request.META = {"HTTP_X_FORWARDED_FOR": "192.168.0.1, 192.168.0.2"}
    ip = apitrack_middleware._get_client_ip(request)  # noqa: SLF001
    assert ip == "192.168.0.1"


def test_get_client_ip_remote_addr(apitrack_middleware):
    request = HttpRequest()
    request.META = {"REMOTE_ADDR": "192.168.0.1"}
    ip = apitrack_middleware._get_client_ip(request)  # noqa: SLF001
    assert ip == "192.168.0.1"


def test_get_client_ip_no_forwarded(apitrack_middleware):
    request = HttpRequest()
    request.META = {}
    ip = apitrack_middleware._get_client_ip(request)  # noqa: SLF001
    assert ip is None


def test_failed_open(apitrack_middleware):
    request = HttpRequest()
    response = HttpResponse()
    request.is_trackable = True
    request.request_id = "test_request_id"
    request.method = "GET"
    request.path = "/test-path"
    request.user = Mock(is_authenticated=True, id=1)
    request.META = {"HTTP_USER_AGENT": "test-agent"}
    response = apitrack_middleware.process_response(request, response)
    assert response.status_code == 200  # noqa: PLR2004
