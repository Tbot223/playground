# external Modules
import pytest

# internal Modules
from CoreV2 import LogSys

@pytest.fixture(scope="module")
def setup_module(tmp_path_factory):
    """
    Fixture to create a LoggerManager instance for testing.
    """
    tmp_path = tmp_path_factory.mktemp("test")
    return LogSys.LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test_logs"), LogSys.Log()

@pytest.mark.usefixtures("setup_module")
class TestLogSys:
    def test_make_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger"
        log_level = "DEBUG"

        # Test creating a logger
        result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert result.success, f"Logger creation failed: {result.error}"
        assert logger_name in logger_manager._loggers.keys(), "Logger not found in manager after creation."

        # Test creating the same logger again
        result_duplicate = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert not result_duplicate.success, "Duplicate logger creation should have failed."

    def test_get_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger_get"
        log_level = "INFO"

        # Get logger ( already created )
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert not get_result.success, "Getting non-existent logger should have failed."

    def test_logger_functionality(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "functional_logger"
        log_level = "INFO"

        # Create logger
        create_result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert create_result.success, f"Logger creation failed: {create_result.error}"

        # Get logger
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert get_result.success, f"Getting logger failed: {get_result.error}"
        logger = get_result.data

        # Test logging
        try:
            logger.info("This is an info message for testing.")
            logger.debug("This is a debug message for testing.")
            logger.error("This is an error message for testing.")
        except Exception as e:
            pytest.fail(f"Logging functionality failed with exception: {e}")

@pytest.mark.usefixtures("setup_module")
class TestLogSysEdgeCases:
    def test_invalid_log_level(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "invalid_level_logger"
        invalid_log_level = "INVALID_LEVEL"

        # Test creating a logger with invalid log level
        result = logger_manager.make_logger(logger_name=logger_name, log_level=invalid_log_level)
        assert not result.success, "Logger creation with invalid log level should have failed."

if __name__ == "__main__":
    pytest.main([__file__])