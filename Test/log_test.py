# external modules
import pytest
import os
import sys
import logging
from pathlib import Path

# internal modules
from Core import log 

@pytest.fixture(scope="function")
def setup_logger(tmp_path):
    tmp_log_dir = tmp_path / "logs"
    logger = log.LoggerManager(name="test_logger", base_dir=str(tmp_log_dir))
    return logger, tmp_log_dir  

@pytest.mark.usefixtures("setup_logger")
class TestLoggerManager:
    def test_get_logger(self, setup_logger):
        logger_manager, log_dir = setup_logger
        logger = logger_manager.get_logger()
        
        # Test if logger is an instance of logging.Logger
        assert isinstance(logger, logging.Logger)
        
        # Test logging to file
        test_message = "This is a test log message."
        logger.info(test_message)
        
        # Check if log file is created
        log_files = list(log_dir.glob("test_logger_*.log"))
        assert len(log_files) == 1, "Log file was not created."
        
        # Check if the log message is in the log file
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert test_message in log_content, "Log message not found in log file."

if __name__ == "__main__":
    pytest.main([__file__, "-v"])