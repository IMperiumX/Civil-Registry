import datetime
import logging
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from django.db import models

from .constants import GOVERNORATES_MAPPING
from .exceptions import InvalidBirthDateError
from .exceptions import InvalidCenturyDigitError
from .exceptions import InvalidGovernorateCodeError
from .exceptions import InvalidNationalIDError

logger = logging.getLogger("core")


@dataclass(frozen=True)
class NationalID(ABC):
    id_number: str
    birth_date: datetime.date | None = None
    governorate: str | None = None
    gender: str | None = None

    @abstractmethod
    def validate(self):
        """Validates the National ID."""

    @abstractmethod
    def extract_birth_date(self):
        """
        Extracts the birth date from the National ID.

        Raises:
            ValueError: If the birth date is invalid.
        """

    @abstractmethod
    def extract_governorate(self):
        """
        Extracts the governorate from the National ID.

        Raises:
            KeyError: If the governorate code is not found.
        """

    @abstractmethod
    def extract_gender(self):
        """
        Extracts the gender from the National ID.
        """


class EgyptianNationalID(NationalID):
    """
    Represents an Egyptian National ID.

    The ID is a 14-digit number with the following format:
        - 1st digit: Century digit (2 for 19XX, 3 for 20XX)
        - 2nd-7th digits: Date of birth (YYMMDD)
        - 8th-9th digits: Governorate code
        - 10th-13th digits: Serial number
        - 14th digit: Check digit
    ref: https://en.wikipedia.org/wiki/Egyptian_National_Identity_Card
    """

    ID_LENGTH = 14
    ID_REGEX = re.compile(r"^\d{14}$")  # 14-digit number

    MIN_CENTURY_DIGIT = 2
    MAX_CENTURY_DIGIT = 3

    def __init__(self, id_number: str):
        logger.debug("Creating EgyptianNationalID object for: %s", id_number)
        super().__init__(id_number=id_number)
        # Ensure the ID is valid
        self.validate()

        # Extract the information from the National ID
        object.__setattr__(self, "birth_date", self.extract_birth_date())
        object.__setattr__(self, "governorate", self.extract_governorate())
        object.__setattr__(self, "gender", self.extract_gender())

    def validate(self):
        """Validates the Egyptian National ID."""
        logger.debug("Validating Egyptian National ID: %s", self.id_number)
        id_match = re.match(self.ID_REGEX, str(self.id_number))
        if not id_match:
            raise InvalidNationalIDError(self.id_number, self.ID_LENGTH)

        object.__setattr__(self, "id_number", id_match.group())

        century_digit = int(self.id_number[0])
        if century_digit not in (self.MIN_CENTURY_DIGIT, self.MAX_CENTURY_DIGIT):
            raise InvalidCenturyDigitError(century_digit)

        logger.debug("Egyptian National ID validation successful: %s", self.id_number)

    def extract_birth_date(self):
        """Extracts the birth date from the National ID."""
        century_digit = int(self.id_number[0])
        year = int(self.id_number[1:3])
        month = int(self.id_number[3:5])
        day = int(self.id_number[5:7])

        if century_digit == self.MIN_CENTURY_DIGIT:
            year += 1900
        else:
            year += 2000

        try:
            logger.debug("Extracted birth date: %s-%s-%s", year, month, day)
            return datetime.date(year, month, day)
        except ValueError as e:
            raise InvalidBirthDateError(year, month, day) from e

    def extract_governorate(self):
        """Extracts the governorate code."""
        gov_code = self.id_number[7:9]
        governorate = GOVERNORATES_MAPPING.get(gov_code)
        if governorate is None:
            logger.warning("Governorate code not found: %s", gov_code)
            raise InvalidGovernorateCodeError(gov_code)
        logger.debug("Extracted governorate: %s", governorate)
        return governorate

    def extract_gender(self):
        """Determines the gender based on the National ID."""
        gender_digit = int(self.id_number[12])
        gender = "Female" if gender_digit % 2 == 0 else "Male"
        logger.debug("Extracted gender: %s", gender)
        return gender


class ApiCall(models.Model):
    id_number = models.CharField(max_length=14, blank=True, default="")
    detail = models.TextField(blank=True, default="")

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    request_id = models.UUIDField(null=True, blank=True, db_index=True)
    request_method = models.CharField(max_length=10)
    path = models.CharField(max_length=255, db_index=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    status_code = models.IntegerField()
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    processing_time = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"{self.timestamp} - {self.request_method} {self.path} - {self.status_code}"
        )
