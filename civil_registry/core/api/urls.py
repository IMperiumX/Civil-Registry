from django.urls import path

from .views import NationalIDView

urlpatterns = [
    path("validate/", NationalIDView.as_view(), name="validate_national_id"),
]
