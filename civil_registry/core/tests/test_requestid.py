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
