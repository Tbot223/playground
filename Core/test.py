# external modules

# internal modules
import AppCore
import StorageManager
from Result import Result
from log import LoggerManager

class CodeTest:
    """
    코드 테스트 클래스
    """
    def __init__(self):
        self.logger = LoggerManager().get_logger()
        self.logger.info("Logger initialized.")

    def AppCoreTest(self):
        """
        AppCore 모듈 테스트
        """
        Core = AppCore.AppCore()
        FileManager = AppCore.FileManager()
        exception_tracker = AppCore.ExceptionTracker()

        testing_data = {"a": 1, "b": "c", "c": 2, "d": 1, "e": 0, "f": 0.3, "g": "d", "h":"g"}
        self.logger.info("Starting AppCore.find_keys_by_value() tests...")
        for comparison_type in ["above", "below", "equal"]:
            int_test = Core.find_keys_by_value(testing_data, 1, comparison_type)
            str_test = Core.find_keys_by_value(testing_data, "c", comparison_type)
            float_test = Core.find_keys_by_value(testing_data, 0.3, comparison_type)

            if not int_test.success: # int_test 실패 시
                self.logger.error(f"(threshold: int)AppCore.find_keys_by_value() test failed for comparison type: {comparison_type}, Error details: {int_test}")
            else:
                self.logger.info(f"(threshold: int)AppCore.find_keys_by_value() test passed for comparison type: {comparison_type}")

            if not str_test.success: # str_test 실패 시
                self.logger.error(f"(threshold: str)AppCore.find_keys_by_value() test failed for comparison type: {comparison_type}, Error details: {str_test}")
            else:
                self.logger.info(f"(threshold: str)AppCore.find_keys_by_value() test passed for comparison type: {comparison_type}")

            if not float_test.success: # float 테스트
                self.logger.error(f"(threshold: float)AppCore.find_keys_by_value() test failed for comparison type: {comparison_type}, Error details: {float_test}")
            else:
                self.logger.info(f"(threshold: float)AppCore.find_keys_by_value() test passed for comparison type: {comparison_type}")
        self.logger.info("AppCore.find_keys_by_value() tests completed.")

    def StorageManagerTest(self):
        """
        StorageManager 모듈 테스트
        """
        # StorageManager.save_data("test_key", {"data": "test_value"})
        result = StorageManager.save_data("test_key", {"data": "test_value"})
        print(result)

CodeTest().AppCoreTest()