# external Modules
import os
from typing import List, Union, Any, Dict, Tuple, Optional
from pathlib import Path
import logging
import time

# internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker

class LoggerManager:
    """
    Logger manager class

    Output logs to log files and console
    """
    def __init__(self, base_dir: Union[str, Path]=None, second_log_dir: str="default"):
        """
        Initialize logger manager

        Args:
            base_dir (Union[str, Path]): Base directory for logs. If None, defaults to '<your_base_dir>/logs'.
            second_log_dir (str): Subdirectory name within the base log directory.
        """
        self._loggers = {}
        # Create log directory
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "logs"
            os.makedirs(base_dir, exist_ok=True)
        self._BASE_DIR = base_dir
        self.second_log_dir = second_log_dir
        self._started_time = time.strftime("%Y-%m-%d_%Hh-%Mm-%Ss", time.localtime())

    def make_logger(self, logger_name: str, log_level: int=logging.INFO, time: Any = None) -> Result:
        """
        Create logger instance
        """
        try:
            # Duplicate check
            if logger_name in self._loggers:
                raise ValueError(f"Logger with name '{logger_name}' already exists.")

            # Always create a new logger instance
            self._loggers[logger_name] = logging.getLogger(logger_name)
            logger = self._loggers[logger_name]
            logger.setLevel(log_level)
            logger.propagate = False  # Prevent duplicate log output

            # Create a log file
            log_filename = self._BASE_DIR / self.second_log_dir / f"{logger_name}_{time or self._started_time}.log"
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)

            # Prevent duplicate handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Set formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # Set file handler
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Set console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            return Result(True, logger, None, f"Logger '{logger_name}' created successfully.")
        except Exception as e:
            return ExceptionTracker().get_exception_return(e)
        
    def get_logger(self, logger_name: str) -> Result:
        """
        Get logger instance by name
        """
        try:
            if logger_name not in self._loggers:
                raise ValueError(f"Logger with name '{logger_name}' does not exist.")
            return Result(True, None, None, self._loggers[logger_name])
        except Exception as e:
            return ExceptionTracker().get_exception_return(e)
        
class Log:
    """
    Log class for logging messages
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize Log class with a logger instance.
        """
        self.logger = logger
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

    def log_message(self, level: Optional[Union[int, str]], message: str) -> Result:
        """
        Log a message with the specified log level.
        """
        if self.logger is None:
            return Result(False, None, None, "Logger is not initialized.")
        try:
            if isinstance(level, str):
                level = self.log_levels.get(level.upper(), logging.INFO)

            self.logger.log(level, message)
            return Result(True, None, None, "Log message sent successfully.")
        except Exception as e:
            return ExceptionTracker().get_exception_return(e) 