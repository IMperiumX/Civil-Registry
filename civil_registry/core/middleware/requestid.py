import logging
import uuid

logger = logging.getLogger("core.requests")


class RequestIDMiddleware:
    """
    Adds a unique request ID to each request for logging and debugging purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # process_view is automatically called by Django
        response = None

        response = self.process_request(request)
        response = response or self.get_response(request)
        return self.process_response(request, response)

    def process_request(self, request):
        """
        Generate a UUID and attach it to the request object.
        """
        request_id = request.headers.get(
            "X-Request-ID",
            uuid.uuid4().hex,
        )  # Get from header or generate

        request.request_id = request_id
        msg = f"Request started: {request.method} {request.path}"
        logger.debug(
            msg,
            extra={"request_id": request_id},
        )

    def process_response(self, request, response):
        """
        Log the request ID, method, path, and status code.
        """
        request_id = getattr(request, "request_id", "unknown")
        msg = f"Request finished: {request.method} {request.path}, Status: {response.status_code}"
        logger.debug(
            msg,
            extra={"request_id": request_id},
        )
        return response

    def process_exception(self, request, exception):
        """
        Log the request ID and exception details if an exception occurs.
        """
        request_id = getattr(request, "request_id", "unknown")
        msg = f"Exception during request: {request_id}, Exception: {exception}"
        logger.exception(msg)
