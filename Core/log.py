# external modules
import logging
import time
import os
from pathlib import Path
from typing import Union

# internal modules
from Core import AppCore, Result

ExceptionTracker = AppCore.ExceptionTracker()

class LoggerManager:
    """
    Logger manager class

    Output logs to log files and console
    """
    def __init__(self, name: str="test", base_dir: Union[str, Path]="<your_base_dir>/logs | ManualPath"):
        """
        Initialize logger manager
        """

        # 로거를 얻기 전에 이름 및 기타 속성을 저장
        if isinstance(base_dir, str) and base_dir.startswith("<your_base_dir>"):
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "/logs")
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory: {e}")
        self._name = name
        self._base_dir = base_dir
        self._setup_logger()

    def _setup_logger(self):
        """
        Set up logger with handlers
        """
        # 항상 새로운 로거 인스턴스 생성
        self.logger = logging.getLogger(self._name)
        self.logger.setLevel(logging.DEBUG)
        
        # 핸들러가 있으면 모두 제거 (이전 핸들러 정리)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 로그 디렉토리 생성
        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir, exist_ok=True)

        # 로그 파일명 생성
        today = time.strftime("%Y-%m-%d,%Hh-%Mm-%Ss", time.localtime()).split(",")
        self._log_filename = os.path.join(self._base_dir, f"{self._name}_{today[0]}_{today[1]}.log")

        # 포맷터 설정
        formatter = logging.Formatter('%(asctime)s : [%(name)s] - [%(levelname)s] : %(message)s')

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 파일 핸들러 추가
        try:
            file_handler = logging.FileHandler(self._log_filename, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error creating file handler: {e}")

    def get_logger(self) -> logging.Logger:
        """
        Return logger object
        """
        # 핸들러가 없으면 다시 설정
        if not self.logger.handlers:
            self._setup_logger()
            
        return self.logger
    


# Example usage:

# logger = LoggerManager().get_logger()
# logger.info("Log system initialized.")