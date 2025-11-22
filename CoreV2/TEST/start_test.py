# external Modules

# internal Modules
from CoreV2.TEST.SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test

class Test_CoreV2:
    def test_AppCore(self):
        pass

    def test_Exception(self):
        pass

    def test_LogSys(self):
        pass

    def test_Utils(self):
        pass

    def test_FileManager(self):
        pass

    def run_all_tests(self):
        AppCore_test.run_tests()
        Exception_test.run_tests()
        LogSys_test.run_tests()
        Utils_test.run_tests()
        FileManager_test.run_tests()

if __name__ == "__main__":
    tester = Test_CoreV2()
    tester.run_all_tests()