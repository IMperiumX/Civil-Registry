from unittest.mock import patch


def test_process_request_generates_request_id(requestid_middleware, requestid_request):
    requestid_middleware.process_request(requestid_request)
    assert hasattr(requestid_request, "request_id")
    assert len(requestid_request.request_id) == 32  # UUID4 hex length


def test_process_request_uses_header_request_id(
    requestid_middleware,
    requestid_request,
):
    requestid_request.headers["X-Request-ID"] = "test-request-id"
    requestid_middleware.process_request(requestid_request)
    assert requestid_request.request_id == "test-request-id"


@patch("civil_registry.core.middleware.requestid.logger")
def test_process_request_logs_request(
    mock_logger,
    requestid_middleware,
    requestid_request,
):
    requestid_middleware.process_request(requestid_request)
    mock_logger.debug.assert_called_once_with(
        "Request started: %s %s",
        requestid_request.method,
        requestid_request.path,
        extra={"request_id": requestid_request.request_id},
    )


@patch("civil_registry.core.middleware.requestid.logger")
def test_process_response_logs_response(
    mock_logger,
    requestid_middleware,
    requestid_request,
    response,
):
    requestid_middleware.process_request(requestid_request)
    mock_logger.reset_mock()  # Reset the mock to clear the previous call
    requestid_middleware.process_response(requestid_request, response)
    mock_logger.debug.assert_called_once_with(
        "Request finished: %s %s, Status: %s",
        requestid_request.method,
        requestid_request.path,
        response.status_code,
        extra={"request_id": requestid_request.request_id},
    )
