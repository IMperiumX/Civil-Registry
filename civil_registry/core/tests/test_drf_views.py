import uuid

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestNationalIDView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",  # noqa: S106
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        settings.MIDDLEWARE += [
            "civil_registry.core.middleware.requestid.RequestIDMiddleware",
        ]  # to attach request_id to request object

    def test_valid_national_id(self):
        request_id = str(uuid.uuid4())
        response = self.client.post(
            "/api/validate/",
            {"id_number": "29001011234567"},
            format="json",
            headers={"x-request-id": request_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "is_valid" in response.data

    def test_invalid_national_id(self):
        request_id = str(uuid.uuid4())
        response = self.client.post(
            "/api/validate/",
            {"id_number": "invalid_id_number"},
            format="json",
            headers={"x-request-id": request_id},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data
