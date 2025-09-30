# external modules
import logging
import time
import os

# internal modules
from Core import AppCore
from .Result import Result

ExceptionTracker = AppCore.ExceptionTracker()

class LoggerManager:
    """
    로거 매니저 클래스

    로그 파일과 콘솔에 로그를 출력
    """
    def __init__(self, name="test", base_dir="/logs"):
        """
        로거 매니저 초기화
        """
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not os.path.exists(base_dir):
            os.makedirs(f"{parent_dir}{base_dir}", exist_ok=True)
        today = time.strftime("%Y-%m-%d,%Hh-%Mm-%Ss", time.localtime()).split(",")
        log_filename = os.path.join(f"{parent_dir}{base_dir}/{name}_{today[0]}_{today[1]}.log")

        formatter = logging.Formatter('%(asctime)s : [%(name)s] - [%(levelname)s] : %(message)s')

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 파일 핸들러
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)

        # 중복 핸들러 방지
        if not self.logger.hasHandlers():
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        로거 객체 반환
        """
        return self.logger
    


# Example usage:
# logger = LoggerManager().get_logger()
# logger.info("Log system initialized.")