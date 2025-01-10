from django.core.validators import RegexValidator
from rest_framework import serializers

from civil_registry.core.models import EgyptianNationalID


class NationalIDInputSerializer(serializers.Serializer):
    id_number = serializers.CharField(
        validators=[
            RegexValidator(
                EgyptianNationalID.ID_REGEX,
                "National ID must be a 14-digit number.",
            ),
        ],
    )

    class Meta:
        fields = ["id_number"]


class NationalIDSerializer(serializers.Serializer):
    is_valid = serializers.SerializerMethodField()
    id_number = serializers.CharField()
    birth_date = serializers.DateField(required=False)
    governorate = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    detail = serializers.CharField(default="")

    class Meta:
        fields = [
            "is_valid",
            "id_number",
            "birth_date",
            "governorate",
            "gender",
            "detail",
        ]

    def get_is_valid(self, obj):
        return not bool(obj.get("detail"))
