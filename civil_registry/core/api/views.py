import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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

    rate_limits = {
        "POST": {
            RateLimitCategory.IP: RateLimit(limit=5, window=1),
            RateLimitCategory.USER: RateLimit(limit=5, window=86400),
        },
    }
    track_endpoint = True

    def post(self, request):
        # XXX: Could be moved to a Middleware to enforce rate limits
        rate_limit = self.rate_limits.get("POST", {}).get(RateLimitCategory.USER)
        ratelimiter = RedisRateLimiter()
        limit = rate_limit.limit
        if limit and ratelimiter.is_limited(
            f"id-validate:{request.user.id}",
            limit=limit,
            window=rate_limit.window,  # 10 per day should be fine
        ):
            ratelimiter.reset(f"id-validate:{request.user.id}")
            return Response(
                {
                    "detail": "You are attempting to create too many organizations too quickly.",
                },
                status=429,
            )

        try:
            data = {
                "is_valid": False,
                "id_number": request.data.get("id_number"),
                "detail": "",
            }

            serializer = NationalIDInputSerializer(data=request.data)

            if not serializer.is_valid():
                data["detail"] = serializer.errors.get("id_number")[0]
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            id_number = serializer.validated_data["id_number"]
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
