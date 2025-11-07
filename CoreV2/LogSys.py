# external Modules
import os
from typing import List, Union, Any, Dict, Tuple
from pathlib import Path
import logging
import time

# internal Modules
from CoreV2.Result import Result

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
        # 로그 디렉토리 생성
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "logs"
            os.makedirs(base_dir, exist_ok=True)
        self._base_dir = base_dir
        self.second_log_dir = second_log_dir
        self._started_time = time.strftime("%Y-%m-%d_%Hh-%Mm-%Ss", time.localtime())

    def make_logger(self, logger_name: str, log_level: int=logging.INFO, time: Any = None) -> Result:
        """
        Create logger instance
        """
        try:
            # 중복 체크
            if logger_name in self._loggers:
                raise ValueError(f"Logger with name '{logger_name}' already exists.")

            # 항상 새로운 로거 인스턴스 생성
            self._loggers[logger_name] = logging.getLogger(logger_name)
            logger = self._loggers[logger_name]
            logger.setLevel(log_level)
            logger.propagate = False  # 중복 로그 출력을 방지

            # 로그 파일명 생성
            log_filename = f"{self._base_dir}/{self.second_log_dir}/{time or self._started_time}_log/{logger_name}.log"
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)

            # 핸들러 중복 방지
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # 포맷터 설정
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # 파일 핸들러 설정
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # 콘솔 핸들러 설정
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            return Result(True, logger, None, f"Logger '{logger_name}' created successfully.")
        except Exception as e:
            return Result(False, None, e, f"Failed to create logger '{logger_name}': {str(e)}")