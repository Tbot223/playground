# external modules
import logging
import time
import os
from pathlib import Path
from typing import Union, Any

# internal modules
from Core import Result
from Core.Exception import ExceptionTracker

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
        self._exception_tracker = ExceptionTracker()
        # 로그 디렉토리 생성
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "logs"
            os.makedirs(base_dir, exist_ok=True)
        self._base_dir = base_dir
        self._log_filename = None
        self.second_log_dir = second_log_dir
        self._started_time = time.strftime("%Y-%m-%d_%Hh-%Mm-%Ss", time.localtime())

    def Make_logger(self, name: str="TEST", time: Any = None) -> Result:
        """
        Create logger instance
        """
        try:
            # 중복 체크
            if name in self._loggers:
                raise ValueError(f"Logger with name '{name}' already exists.")

            # 항상 새로운 로거 인스턴스 생성
            self._loggers[name] = logging.getLogger(name)
            logger = self._loggers[name]
            logger.setLevel(logging.DEBUG)
            logger.propagate = False  # 중복 로그 출력을 방지

            # 로그 파일명 생성
            self._log_filename = f"{self._base_dir}/{self.second_log_dir}/{self._started_time if time is None else time}_log/{name}.log"
            os.makedirs(os.path.dirname(self._log_filename), exist_ok=True)

            # 핸들러 중복 방지
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # 포맷터 설정
            formatter = logging.Formatter('%(asctime)s : [%(name)s] - [%(levelname)s] : %(message)s')

            # 콘솔 핸들러 추가
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # 파일 핸들러 추가
            file_handler = logging.FileHandler(self._log_filename, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            return Result(True, None, None, True)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def get_logger(self, name="TEST") -> logging.Logger:
        """
        Return logger object
        """
        try:
            if name not in self._loggers:
                raise ValueError(f"Logger with name '{name}' does not exist. Please create it first using Make_logger method.")
            else:
                return Result(True, None, None, self._loggers[name])
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
class Log:
    """
    Log class

    Provides logging utilities
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize log class
        """
        self.logger = logger
        self._exception_tracker = ExceptionTracker()
        self.log_levels = {
                "info" : self.logger.info,
                "error" : self.logger.error,
                "debug" : self.logger.debug,
                "warning" : self.logger.warning
            }

    def log_msg(self, level: str, message: str, no_log: bool=False):
        """
        Function to log messages at different levels
        """
        try:
            if not isinstance(message, str) or not isinstance(level, str) or not isinstance(no_log, bool):
                raise ValueError("Invalid input types for log_msg function.")
            if no_log:
                return Result(True, None, "Logging is disabled", False)
            log_level = level.lower()
            if log_level in self.log_levels:
                self.log_levels[log_level](message)
            else:
                raise ValueError(f"Invalid log level: {log_level}. Use 'info', 'error', 'debug', or 'warning'.")
            return Result(True, None, None, True)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

# Example usage:


# if __name__ == "__main__":
#     logger_manager = LoggerManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"))
#     logger_manager.Make_logger("ExampleLogger")
#     logger_manager.Make_logger("AnotherLogger")
#     logger = logger_manager.get_logger("ExampleLogger")
#     logger2 = logger_manager.get_logger("AnotherLogger")
#     logger.info("This is a info message.")
#     logger.error("This is a error message.")
#     logger.debug("This is a debug message.")
#     logger.warning("This is a warning message.")
#     logger2.info("This is a info message.")