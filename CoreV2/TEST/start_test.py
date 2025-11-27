# external Modules
import pytest
from pathlib import Path

# internal Modules
from CoreV2.TEST.SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test
from CoreV2 import FileManager

class Test_CoreV2:
    def test_AppCore(self):
        pytest.main([AppCore_test.__file__])

    def test_Exception(self):
        pytest.main([Exception_test.__file__])

    def test_LogSys(self):
        pytest.main([LogSys_test.__file__])

    def test_Utils(self):
        pytest.main([Utils_test.__file__])

    def test_FileManager(self):
        pytest.main([FileManager_test.__file__])

    def run_all_tests(self):
        pytest.main([str(Path(__file__).parent / "SRC")])

if __name__ == "__main__":
    log_del = input("Do you want to delete the log files after running the test? (**Caution** All existing logs will be deleted) (y/n): ").strip().lower()
    tester = Test_CoreV2()
    tester.run_all_tests()
    if log_del == 'y':
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        with FileManager.FileManager(is_logging_enabled=False) as FM:
            if log_dir.exists() and log_dir.is_dir():
                for item in log_dir.iterdir():
                    FM.delete_directory(item)
            else:
                print(f"No log directory found at: {log_dir}")
