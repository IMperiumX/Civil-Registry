from factory import Faker
from factory.django import DjangoModelFactory

from civil_registry.core.models import ApiCall


class ApiCallFactory(DjangoModelFactory):
    class Meta:
        model = ApiCall

    id_number = "29001011234567"
    request_id = Faker("uuid4")
    user_id = Faker("random_int", min=1, max=1000)
    detail = Faker("text")
    request_method = Faker("http_method")
    path = Faker("uri_path")
    status_code = 200
    client_ip = Faker("ipv4")
    user_agent = Faker("user_agent")
