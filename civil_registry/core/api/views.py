import logging
from dataclasses import asdict
from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from civil_registry.core.exceptions import InvalidBirthDateError
from civil_registry.core.exceptions import InvalidCenturyDigitError
from civil_registry.core.models import EgyptianNationalID
from civil_registry.core.ratelimit import RedisRateLimiter
from civil_registry.core.types import RateLimit
from civil_registry.core.types import RateLimitCategory

from .serializers import NationalIDInputSerializer
from .serializers import NationalIDSerializer

logger = logging.getLogger("core")


class NationalIDView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NationalIDInputSerializer

    rate_limits: dict[str, dict[RateLimitCategory, RateLimit]] = {
        "POST": {
            RateLimitCategory.IP: RateLimit(limit=5, window=1),
            RateLimitCategory.USER: RateLimit(limit=10, window=1),
        },
    }
    track_endpoint: bool = True

    def post(self, request: Request) -> Response:
        try:
            rate_limit: RateLimit = self.rate_limits.get("POST", {}).get(
                RateLimitCategory.USER,
            )
            ratelimiter = RedisRateLimiter()
            limit: int = rate_limit.limit
            window: int = rate_limit.window
            key: str = f"id-validate:{request.user.id}"
            if limit and ratelimiter.is_limited(
                key,
                limit=limit,
                window=window,
            ):
                logger.debug(
                    "core.api.rate-limit.exceeded Key: %s Limit: %s Window: %s",
                    key,
                    limit,
                    window,
                )
                return Response(
                    {
                        "detail": "You are attempting to validate too many IDs. Please try again later.",
                    },
                    status=429,
                )
            data: dict[str, Any] = {
                "is_valid": False,
                "id_number": request.data.get("id_number"),
                "detail": "",
            }

            serializer = NationalIDInputSerializer(data=request.data)

            if not serializer.is_valid():
                data["detail"] = serializer.errors.get("id_number")[0]
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            id_number: str = serializer.validated_data["id_number"]
            egyptian_national_id = EgyptianNationalID(id_number)
            output_serializer = NationalIDSerializer(data=asdict(egyptian_national_id))

            if output_serializer.is_valid():
                return Response(
                    output_serializer.data,
                    status=status.HTTP_200_OK,
                )

            return Response(
                output_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidCenturyDigitError as e:
            data["detail"] = str(e)
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidBirthDateError as e:
            data["detail"] = str(e)
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST,
            )
