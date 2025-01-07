from django.urls import path

from civil_registry.core.api.views import NationalIDView

urlpatterns = [
    path("national-id/", NationalIDView.as_view(), name="national-id"),
]
