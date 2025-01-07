from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from civil_registry.core.constants import MAX_CENTURY_DIGIT
from civil_registry.core.constants import MIN_CENTURY_DIGIT
from civil_registry.core.models import EgyptianNationalID


class NationalIDInputSerializer(serializers.Serializer):
    national_id = serializers.CharField()

    def validate_national_id(self, value):
        if not value.isdigit():
            msg = f"Invalid national ID: {value}. Only digits are allowed."
            raise ValidationError(msg)

        if len(value) != EgyptianNationalID.ID_LENGTH:
            msg = (
                f"Invalid national ID length. "
                f"Expected {EgyptianNationalID.ID_LENGTH} digits.",
            )
            raise ValidationError(msg)

        century_digit = int(value[0])
        if not (MIN_CENTURY_DIGIT <= century_digit <= MAX_CENTURY_DIGIT):
            msg = (
                f"Invalid century digit: {century_digit}. "
                f"Must be between {MIN_CENTURY_DIGIT} and {MAX_CENTURY_DIGIT}.",
            )
            raise ValidationError(msg)

        return value


class NationalIDSerializer(serializers.Serializer):
    is_valid = serializers.SerializerMethodField()
    id_number = serializers.CharField()
    birth_date = serializers.DateField(required=False)
    governorate = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    error_message = serializers.CharField(default=None)

    class Meta:
        fields = [
            "is_valid",
            "id_number",
            "birth_date",
            "governorate",
            "gender",
            "error_message",
        ]

    def get_is_valid(self, obj):
        return not bool(obj.get("error_message"))
