import datetime

import pytest
from django.utils import timezone

from civil_registry.core.exceptions import InvalidBirthDateError
from civil_registry.core.exceptions import InvalidCenturyDigitError
from civil_registry.core.exceptions import InvalidNationalIDError
from civil_registry.core.models import ApiCall
from civil_registry.core.models import EgyptianNationalID

from .factories import ApiCallFactory


def test_valid_egyptian_national_id():
    id_number = "29001011234567"
    national_id = EgyptianNationalID(id_number)
    assert national_id.birth_date == datetime.date(1990, 1, 1)
    assert national_id.governorate == "Dakahlia"
    assert national_id.gender == "Female"


def test_invalid_century_digit():
    id_number = "49805231234567"
    with pytest.raises(InvalidCenturyDigitError):
        EgyptianNationalID(id_number)


def test_invalid_birth_date():
    id_number = "29802291234567"  # Invalid date: February 29, 1998 (not a leap year)
    with pytest.raises(InvalidBirthDateError):
        EgyptianNationalID(id_number)


def test_female_gender():
    id_number = "29805231234568"
    national_id = EgyptianNationalID(id_number)
    assert national_id.gender == "Female"


def test_governorate_extraction():
    id_number = "29805231234567"
    national_id = EgyptianNationalID(id_number)
    assert national_id.governorate == "Dakahlia"


def test_too_long_national_id():
    id_number = "298052312345678"
    with pytest.raises(InvalidNationalIDError):
        EgyptianNationalID(id_number)


def test_invalid_characters():
    id_number = "2980523123456a"
    with pytest.raises(InvalidNationalIDError):
        EgyptianNationalID(id_number)


@pytest.mark.django_db
def test_api_call_creation():
    api_call = ApiCall.objects.create(
        id_number="29805231234567",
        detail="Test detail",
        request_method="GET",
        path="/api/test/",
        status_code=200,
        client_ip="127.0.0.1",
        user_agent="TestAgent",
    )
    assert api_call.id_number == "29805231234567"
    assert api_call.detail == "Test detail"
    assert api_call.request_method == "GET"
    assert api_call.path == "/api/test/"
    assert api_call.status_code == 200  # noqa: PLR2004
    assert api_call.client_ip == "127.0.0.1"
    assert api_call.user_agent == "TestAgent"
    assert api_call.timestamp <= timezone.now()


@pytest.mark.django_db
def test_api_call_ordering():
    api_call1 = ApiCallFactory()
    api_call2 = ApiCallFactory()
    assert list(ApiCall.objects.all()) == [api_call2, api_call1]
