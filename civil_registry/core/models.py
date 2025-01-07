import datetime
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from .constants import GOVERNORATES_MAPPING
from .constants import MIN_CENTURY_DIGIT
from .exceptions import InvalidBirthDateError


@dataclass(frozen=True)
class NationalID(ABC):
    id_number: str
    birth_date: datetime.date = None
    governorate: str = None
    gender: str = None

    def __post_init__(self):
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
    ID_LENGTH = 14

    def extract_birth_date(self):
        """Extracts the birth date from the National ID."""
        year = int(self.id_number[1:3])
        month = int(self.id_number[3:5])
        day = int(self.id_number[5:7])

        year += 2000
        century_digit = int(self.id_number[0])
        if century_digit == MIN_CENTURY_DIGIT:
            year_offset = 100
            year -= year_offset  # old man :D

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
