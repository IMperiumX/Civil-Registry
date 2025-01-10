import logging
import time

from rest_framework import status

from civil_registry.core.tasks import create_api_call_record

logger = logging.getLogger("core.requests")


class APICallTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            view_class = getattr(view_func, "view_class", None)
            if not view_class:
                return

            # Only track specific endpoints that have the `track_endpoint` attribute set to True
            track_endpoint = getattr(view_class, "track_endpoint", False)
            if not track_endpoint:
                return

            request.is_trackable = True
            request.start_time = time.time()
        except Exception:
            logging.exception(
                "Error during API tracking, failing open. THIS SHOULD NOT HAPPEN",
                extra={"request_id": request.request_id},
            )

    def process_response(self, request, response):
        if not (hasattr(request, "is_trackable") and request.is_trackable):
            return response

        try:
            # Handle rate-limited requests (don't track them)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                return response

            # Calculate request processing time
            end_time = time.time()
            processing_time = (
                (end_time - request.start_time) * 1000
                if hasattr(request, "start_time")
                else None
            )

            data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "request_id": request.request_id,
                "request_method": request.method,
                "path": request.path,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "status_code": response.status_code,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "id_number": response.data.get("id_number", ""),
                "detail": response.data.get("detail"),
                "processing_time": processing_time,
            }

            # Asynchronously log the data using Celery
            create_api_call_record.delay(data)
        except Exception:
            logger.exception(
                "Error during API tracking, failing open. THIS SHOULD NOT HAPPEN",
                extra={"request_id": request.request_id},
            )
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
