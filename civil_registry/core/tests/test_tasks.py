from unittest.mock import Mock
from unittest.mock import patch

from civil_registry.core.tasks import create_api_call_record


@patch("civil_registry.core.tasks.ApiCall.objects.create")
def test_create_api_call_record_success(mock_create, api_call_data):
    create_api_call_record(api_call_data)
    mock_create.assert_called_once_with(**api_call_data)


@patch("civil_registry.core.tasks.ApiCall.objects.create")
@patch("civil_registry.core.tasks.logger")
def test_create_api_call_record_exception(mock_logger, mock_create, api_call_data):
    mock_create.side_effect = Exception("Test exception")
    create_api_call_record(api_call_data)
    mock_logger.exception.assert_called_once_with("Error saving API call:")


def test_create_api_call_record_logging(api_call_data):
    logger = Mock()
    with (
        patch("civil_registry.core.tasks.ApiCall.objects.create") as mock_create,
        patch("civil_registry.core.tasks.logger", logger),
    ):
        create_api_call_record(api_call_data)
        logger.info.assert_called_once_with(
            "API call logged: %s Request ID: %s",
            api_call_data["path"],
            api_call_data["request_id"],
        )
        mock_create.assert_called_once_with(**api_call_data)
