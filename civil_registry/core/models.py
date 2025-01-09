import datetime
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from django.conf import settings
from django.db import models

from .constants import GOVERNORATES_MAPPING
from .constants import MAX_CENTURY_DIGIT
from .constants import MIN_CENTURY_DIGIT
from .exceptions import InvalidBirthDateError
from .exceptions import InvalidCenturyDigitError

logger = logging.getLogger("core")


@dataclass(frozen=True)
class NationalID(ABC):
    id_number: str
    birth_date: datetime.date = None
    governorate: str = None
    gender: str = None

    def __post_init__(self):
        logger.debug(f"Creating {self}")
        # Ensure the ID is a string
        object.__setattr__(self, "id_number", str(self.id_number))
        # Extract the information from the National ID
        object.__setattr__(self, "birth_date", self.extract_birth_date())
        object.__setattr__(self, "governorate", self.extract_governorate())
        object.__setattr__(self, "gender", self.extract_gender())

    @abstractmethod
    def extract_birth_date(self):
        pass

    @abstractmethod
    def extract_governorate(self):
        pass

    @abstractmethod
    def extract_gender(self):
        pass


class EgyptianNationalID(NationalID):
    """
    Represents an Egyptian National ID.

    The ID is a 14-digit number with the following format:
        - 1st digit: Century digit (1 for 19XX, 2 for 20XX)
        - 2nd-3rd digits: Year of birth
        - 4th-5th digits: Month of birth
        - 6th-7th digits: Day of birth
        - 8th-9th digits: Governorate code
        - 10th-13th digits: Random number
    ref: https://en.wikipedia.org/wiki/Egyptian_National_Identity_Card
    """

    ID_LENGTH = 14

    def extract_birth_date(self):
        """Extracts the birth date from the National ID."""
        century_digit = int(self.id_number[0])
        if century_digit not in (MIN_CENTURY_DIGIT, MAX_CENTURY_DIGIT):
            raise InvalidCenturyDigitError(century_digit)

        year = int(self.id_number[1:3])
        month = int(self.id_number[3:5])
        day = int(self.id_number[5:7])

        if century_digit == MIN_CENTURY_DIGIT:
            year += 1900
        else:
            year += 2000

        try:
            return datetime.date(year, month, day)
        except ValueError as e:
            raise InvalidBirthDateError(year, month, day) from e

    def extract_governorate(self):
        """Extracts the governorate code (placeholder)."""
        gov_code = self.id_number[7:9]
        return GOVERNORATES_MAPPING.get(gov_code, "Dawlat Tanta")

    def extract_gender(self):
        """Determines the gender based on the National ID."""
        gender_digit = int(self.id_number[12])
        return "Female" if gender_digit % 2 == 0 else "Male"


class APICall(models.Model):
    # relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # fields
    endpoint = models.CharField(max_length=255)
    id_number = models.CharField(max_length=14, blank=True, default="")
    request_data = models.JSONField(
        null=True,
        blank=True,
    )  # Store request data (optional)
    response_data = models.JSONField(
        null=True, blank=True
    )  # Store response data (optional)
    status_code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.timestamp} - {self.endpoint} - {self.status_code}"
