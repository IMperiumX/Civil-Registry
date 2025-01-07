import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from civil_registry.core.models import EgyptianNationalID

from .serializers import NationalIDInputSerializer
from .serializers import NationalIDSerializer

logger = logging.getLogger(__name__)


class NationalIDView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NationalIDInputSerializer
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)

            if not serializer.is_valid():
                msg = serializer.errors.get("error_message")
                logger.error(msg)
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            national_id = serializer.validated_data["national_id"]
            egyptian_national_id = EgyptianNationalID(national_id)
            output_serializer = NationalIDSerializer(data=asdict(egyptian_national_id))

            if output_serializer.is_valid():
                msg = f"National ID validated: {national_id}"
                logger.info(msg)
                return Response(
                    output_serializer.data,
                    status=status.HTTP_200_OK,
                )

        except Exception:
            msg = "Unexpected error during National ID processing"
            logger.exception(msg)
            return Response(
                {"error": msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
