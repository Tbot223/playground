# external Modules
import pytest
from pathlib import Path

# internal Modules
from CoreV2.TEST.SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test

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
    tester = Test_CoreV2()
    tester.run_all_tests()