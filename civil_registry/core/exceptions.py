import logging

from rest_framework.views import exception_handler

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


class InvalidNationalIDError(Exception):
    """Raised when the national ID length is invalid."""

    def __init__(self, id_number, expected_length):
        self.id_number = id_number
        self.expected_length = expected_length
        super().__init__(
            "National ID must be a 14-digit number. But got %s.",
            id_number,
        )


class InvalidCenturyDigitError(Exception):
    """Raised when the century digit is invalid."""

    def __init__(self, century_digit):
        self.century_digit = century_digit
        super().__init__(
            f"Invalid century digit: {century_digit}. Must be between 2 and 3.",
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
