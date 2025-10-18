# external modules
import os
from pathlib import Path

# internal modules
from Core import AppCore, Result, log

class DebugTool:
    """
    Debug tool class

    Provides debugging utilities
    """
    def __init__(self, logger = None):
        """
        Initialize debug tool

        Args:
            logger: LoggerManager instance for logging
        """
        self.exception_tracker = AppCore.ExceptionTracker()
        self.LoggerManager = log.LoggerManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"))
        if logger is None:
            print("No logger provided, initializing default LoggerManager.")
            self.logger = self.LoggerManager.Make_logger(name="DebugTool")
        else:
            self.logger = logger

    def debug_log(self, message: str, isDebug: bool):
        """
        (Debug) Function to log debug messages if isDebug is True
        """
        try:
            if isDebug:
                self.logger.debug(message)
                return Result(True, None, None, None)
            return Result(True, None, "Debug is disabled", None)
        except Exception as e:
            print(f"Error in debug_log function: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)