import contextlib

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "civil_registry.core"

    def ready(self):
        with contextlib.suppress(ImportError):
            import civil_registry.core.signals  # noqa: F401
