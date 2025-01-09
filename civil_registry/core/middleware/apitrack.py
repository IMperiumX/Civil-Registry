import json
import logging

from civil_registry.core.models import APICall

logger = logging.getLogger("core")


class APICallTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only track specific endpoints, e.g., NationalIDView
        try:
            view_class = getattr(view_func, "view_class", None)
            if not view_class:
                return

            track_endpoint = getattr(view_class, "track_endpoint", False)
            if not track_endpoint:
                return
            request.api_call_data = {
                "endpoint": request.path,
                "request_data": json.loads(request.body),
            }
        except Exception:
            logging.exception(
                "Error during API tracking, failing open. THIS SHOULD NOT HAPPEN",
            )

    def process_response(self, request, response):
        if hasattr(request, "api_call_data"):
            api_call_data = request.api_call_data
            status_code = response.status_code

            id_number = None
            detail = ""
            response_data = None

            if hasattr(response, "data"):
                response_data = response.data
                id_number = response.data.get("id_number")
                detail = response.data.get("detail")

            try:
                APICall.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    endpoint=api_call_data["endpoint"],
                    id_number=id_number,
                    request_data=api_call_data["request_data"],
                    response_data=response_data,
                    status_code=status_code,
                    detail=detail,
                )
            except Exception:
                logger.exception("Error saving APICall:")

        return response
