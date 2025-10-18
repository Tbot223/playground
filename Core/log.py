# external modules
import logging
import time
import os
from pathlib import Path
from typing import Union

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
        self.exception_tracker = ExceptionTracker()
        # 로그 디렉토리 생성
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "/logs")
            os.makedirs(base_dir, exist_ok=True)
        self._base_dir = base_dir
        self._log_filename = None
        self.second_log_dir = second_log_dir

    def Make_logger(self, name: str="TEST"):
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
            today = time.strftime("%Y-%m-%d,%Hh-%Mm-%Ss", time.localtime()).split(",")
            self._log_filename = f"{self._base_dir}/{self.second_log_dir}_{today[0]}_{today[1]}/{name}.log"
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
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def get_logger(self, name="TEST") -> logging.Logger:
        """
        Return logger object
        """
        try:
            if name not in self._loggers:
                raise ValueError(f"Logger with name '{name}' does not exist. Please create it first using Make_logger method.")
            else:
                return self._loggers[name]
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        



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