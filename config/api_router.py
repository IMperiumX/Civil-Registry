from django.urls import path

from civil_registry.core.api.views import NationalIDView

urlpatterns = [
    path("validate/", NationalIDView.as_view(), name="validate_national_id"),
]
