import logging

from rest_framework.views import exception_handler

from .constants import MAX_CENTURY_DIGIT
from .constants import MIN_CENTURY_DIGIT

logger = logging.getLogger("core")


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        logger.exception(
            response.data,
            extra={"request_id": context["request"].request_id},
        )
    return response


class InvalidNationalIDLengthError(Exception):
    """Raised when the national ID length is invalid."""

    def __init__(self, id_number, expected_length):
        self.id_number = id_number
        self.expected_length = expected_length
        super().__init__(
            f"Invalid national ID length: {len(id_number)}. "
            f"Expected {expected_length} digits.",
        )


class InvalidNationalIDCharactersError(Exception):
    """Raised when the national ID contains invalid characters."""

    def __init__(self, id_number):
        self.id_number = id_number
        super().__init__(f"Invalid national ID: {id_number}. Only digits are allowed.")


class InvalidCenturyDigitError(Exception):
    """Raised when the century digit is invalid."""

    def __init__(self, century_digit):
        self.century_digit = century_digit
        super().__init__(
            f"Invalid century digit: {century_digit}. "
            f"Must be between {MIN_CENTURY_DIGIT} and {MAX_CENTURY_DIGIT}.",
        )


class InvalidBirthDateError(Exception):
    """Raised when the birth date is invalid."""

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
        super().__init__(f"Invalid birth date: {year}-{month}-{day}.")


class InvalidConfigurationError(Exception):
    pass
