# external Modules
import pytest

# internal Modules
from CoreV2 import AppCore

@pytest.fixture(scope="module")
def test_appcore_initialization():
    app_core = AppCore.AppCore()
    return app_core

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization")
class TestAppCore:
    def test_initialization(self, test_appcore_initialization):
        assert test_appcore_initialization is not None
        assert isinstance(test_appcore_initialization, AppCore.AppCore)

    def test_thread_pool_executor(self, test_appcore_initialization):
        def executor_task(x):
            return x * x
        
        tasks = [(executor_task, {"x": i+1}) for i in range(100)]
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=2, override=False, timeout=1)
        
        for i, result in enumerate(results.data):
            assert result.data == (i+1) * (i+1)

    def process_pool_executor_task(self, x):
        return x + 10

    def test_process_pool_executor(self, test_appcore_initialization):
        tasks = [(self.process_pool_executor_task, {"x": i+1}) for i in range(100)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=2, override=False, timeout=1)
        
        for i, result in enumerate(results.data):
            assert result.data == (i+1) + 10

if __name__ == "__main__":
    pytest.main([__file__])