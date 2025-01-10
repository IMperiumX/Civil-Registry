import logging

from celery import shared_task

from civil_registry.core.models import ApiCall

logger = logging.getLogger(__name__)


@shared_task
def create_api_call_record(data):
    try:
        ApiCall.objects.create(**data)
        logger.info(
            "API call logged: %s Request ID: %s",
            data["path"],
            data["request_id"],
        )
    except Exception:
        logger.exception("Error saving API call:")
