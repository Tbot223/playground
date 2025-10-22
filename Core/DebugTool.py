# external modules
import os
from pathlib import Path

# internal modules
from Core import Result
from Core.Exception import ExceptionTracker

class DebugTool:
    """
    Debug tool class

    Provides debugging utilities
    """
    def __init__(self, logger):
        """
        Initialize debug tool

        Args:
            logger: LoggerManager instance for logging
        """
        self.exception_tracker = ExceptionTracker()
        self.logger = logger

    def debug_log(self, message: str, isDebug: bool):
        """
        (Debug) Function to log debug messages if isDebug is True
        """
        try:
            if isDebug:
                self.logger.debug(message)
                return Result(True, None, None, True)
            return Result(True, None, "Debug is disabled", False)
        except Exception as e:
            print(f"Error in debug_log function: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)