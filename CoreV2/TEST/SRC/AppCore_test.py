# external Modules
import pytest
import random
from typing import Callable, Dict, List, Tuple, Any, Union, Optional
import subprocess

# internal Modules
from CoreV2 import AppCore

@pytest.fixture(scope="module")
def test_appcore_initialization():
    """
    Fixture to initialize AppCore instance for testing.
    """
    app_core = AppCore.AppCore()
    return app_core

@pytest.fixture(scope="module")
def helper_methods():
    """
    Fixture to provide helper methods for testing.
    """
    return HelperMethods()

class HelperMethods:
    def metrix_task(self, n: int, m: int) -> bool:
        """
        A sample task that generates an n x m matrix filled with random floats.
        """
        [[random.random() for _ in range(m)] for _ in range(n)]
        return True
    
    def verify_results(self, results: List[Any], expected_count: int = 500) -> None:
        """
        Verify that the results list contains the expected number of successful results.
        """
        assert len(results) == expected_count
        for res in results:
            assert res.success is True
            assert res.data is True

    def dummy_task(self, x) -> str:
        """
        A simple dummy task that returns a formatted string.
        """
        return f"dummy, {x}"
    
@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCore:
    def test_initialization(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the initialization of the AppCore class.
        """
        assert test_appcore_initialization is not None
        assert isinstance(test_appcore_initialization, AppCore.AppCore)

    def test_HelperMethods_initialization(self, helper_methods: HelperMethods) -> None:
        """
        Test the initialization of the HelperMethods class.
        """
        assert helper_methods is not None
        assert isinstance(helper_methods, HelperMethods)

    # Test Methods
    def test_thread_pool_executor(self, test_appcore_initialization: AppCore.AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the thread pool executor with 500 tasks.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(50)]
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=4, override=False, timeout=1)
        helper_methods.verify_results(results.data, expected_count=50)
    
    def test_process_pool_executor(self, test_appcore_initialization: AppCore.AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the process pool executor with 500 tasks.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(50)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=4, override=False, timeout=1, chunk_size=10)
        helper_methods.verify_results(results.data, expected_count=50)

    def test_find_keys_by_value(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the find_keys_by_value method for both nested and non-nested dictionaries.
        """
        # Non-nested dictionary test
        sample_dict = {'a': 1, 'b': 2, 'c': 1, 'd': 3}
        keys = test_appcore_initialization.find_keys_by_value(sample_dict, 1, "eq", False).data
        assert set(keys) == {'a', 'c'}

        # Nested dictionary test
        sample_dict_nested = {'a': 1, 'b': {'b1': 2, 'b2': 1}, 'c': 1, 'd': 3}
        keys_nested = test_appcore_initialization.find_keys_by_value(sample_dict_nested, 1, "eq", True).data
        assert set(keys_nested) == {'a', 'b.b2', 'c'}

    def test_get_text_by_lang(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the get_text_by_lang method for retrieving text based on language code.
        """
        not_supported_lang = test_appcore_initialization.get_text_by_lang("Test Key", "fr")
        assert not_supported_lang.data == "This is a test value" # Default to 'en' text

        test_appcore_initialization._default_lang = "ko"
        not_supported_lang_ko = test_appcore_initialization.get_text_by_lang("Test Key", "de")
        assert not_supported_lang_ko.data == "이것은 테스트 값입니다." # Default to 'ko' text

        supported_lang = test_appcore_initialization.get_text_by_lang("Test Key", "en")
        assert supported_lang.data == "This is a test value" # Supported 'en' text

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCoreXfail:
    def _dummy_task(self, x) -> str:
        return f"dummy, {x}"
    
    def test_thread_pool_executor(self, test_appcore_initialization: AppCore.AppCore):
        """
        Test various failure scenarios for the thread pool executor.
        """
        empty_tasks_result = test_appcore_initialization.thread_pool_executor([], workers=4, override=False, timeout=1)
        assert empty_tasks_result.success is False
        assert "Data must be a non-empty list" in empty_tasks_result.error

        wrong_tasks_result_func = test_appcore_initialization.thread_pool_executor([("not_a_function", {"x" : 1})], workers=4, override=True, timeout=1)
        wrong_tasks_result_kwargs = test_appcore_initialization.thread_pool_executor([(self._dummy_task, "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_both = test_appcore_initialization.thread_pool_executor([("not_a_function", "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_not_tuple = test_appcore_initialization.thread_pool_executor([[self._dummy_task, {"x" : 1}]], workers=4, override=True, timeout=1)
        wrong_tasks_result_one_tuple = test_appcore_initialization.thread_pool_executor([(self._dummy_task)], workers=4, override=True, timeout=1)
        for result in [wrong_tasks_result_func, wrong_tasks_result_kwargs, wrong_tasks_result_both, wrong_tasks_result_not_tuple, wrong_tasks_result_one_tuple]:
            assert result.success is False
            assert "Each item in data must be a tuple of (function, kwargs_dict)" in result.error

        wrong_workers_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})], workers=0, override=False, timeout=1)
        assert wrong_workers_result.success is False
        assert "workers must be a positive integer" in wrong_workers_result.error
        override_workers_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})]*2, workers=5, override=False, timeout=1)
        assert override_workers_result.success is False
        assert "workers 5 exceeds number of tasks 2" in override_workers_result.error

        wrong_timeout_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=0)
        assert wrong_timeout_result.success is False
        assert "timeout must be a positive number" in wrong_timeout_result.error

    def test_process_pool_executor(self, test_appcore_initialization: AppCore.AppCore):
        """
        Test various failure scenarios for the process pool executor.
        """
        empty_tasks_result = test_appcore_initialization.process_pool_executor([], workers=4, override=False, timeout=1)
        assert empty_tasks_result.success is False
        assert "Data must be a non-empty list" in empty_tasks_result.error

        wrong_tasks_result_func = test_appcore_initialization.process_pool_executor([("not_a_function", {"x" : 1})], workers=4, override=True, timeout=1)
        wrong_tasks_result_kwargs = test_appcore_initialization.process_pool_executor([(self._dummy_task, "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_both = test_appcore_initialization.process_pool_executor([("not_a_function", "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_not_tuple = test_appcore_initialization.process_pool_executor([[self._dummy_task, {"x" : 1}]], workers=4, override=True, timeout=1)
        wrong_tasks_result_one_tuple = test_appcore_initialization.process_pool_executor([(self._dummy_task)], workers=4, override=True, timeout=1)
        for result in [wrong_tasks_result_func, wrong_tasks_result_kwargs, wrong_tasks_result_both, wrong_tasks_result_not_tuple, wrong_tasks_result_one_tuple]:
            assert result.success is False
            assert "Each item in data must be a tuple of (function, kwargs_dict)" in result.error

        wrong_workers_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=0, override=False, timeout=1)
        assert wrong_workers_result.success is False
        assert "workers must be a positive integer" in wrong_workers_result.error
        override_workers_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})]*2, workers=5, override=False, timeout=1)
        assert override_workers_result.success is False
        assert "workers 5 exceeds number of tasks 2" in override_workers_result.error

        wrong_timeout_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=0)
        assert wrong_timeout_result.success is False
        assert "timeout must be a positive number" in wrong_timeout_result.error

        wrong_chunk_size_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=1, chunk_size=0)
        assert wrong_chunk_size_result.success is False
        assert "chunk_size must be a positive integer" in wrong_chunk_size_result.error

    def test_find_keys_by_value(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test failure scenarios for the find_keys_by_value method.
        """
        # Non-dictionary input test
        non_dict_result = test_appcore_initialization.find_keys_by_value("not_a_dict", 1, "eq", False)
        assert non_dict_result.success is False
        assert "Input data must be a dictionary" in non_dict_result.error

        wrong_comparison_result = test_appcore_initialization.find_keys_by_value({'a': 1}, 1, "unsupported_op", False)
        assert wrong_comparison_result.success is False
        assert "Unsupported comparison operator: unsupported_op" in wrong_comparison_result.error

        wrong_threshold_result = test_appcore_initialization.find_keys_by_value({'a': 1}, ['not', 'a', 'valid', 'type'], "eq", False)
        assert wrong_threshold_result.success is False
        assert "Threshold must be of type str, bool, int, or float" in wrong_threshold_result.error

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCoreEdgeCases:
    def test_process_pool_executor_no_chunk(self, test_appcore_initialization: AppCore.AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the process pool executor without specifying chunk size.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        22 tasks are used to test edge case with small number of tasks.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(25)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=4, override=False, timeout=1)
        helper_methods.verify_results(results.data, expected_count=25)

    # I WILL ADD MORE EDGE CASE TESTS HERE IN THE FUTURE

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization")
class TestCLIMethods:
    def test_clear_console(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the clear_console method to ensure it executes without errors.
        """
        try:
            test_appcore_initialization.clear_console()
        except Exception as e:
            pytest.fail(f"clear_console raised an exception: {e}")

    def test_exit_application(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the exit_application method to ensure it executes without errors.
        """
        with pytest.raises(SystemExit) as exc_info:
            test_appcore_initialization.exit_application(code=0)
        assert exc_info.value.code == 0

    def test_restart_application(self, test_appcore_initialization: AppCore.AppCore) -> None:
        """
        Test the restart_application method to ensure it executes without errors.
        """
        proc = subprocess.run(["python", "-c", "import sys; from CoreV2.AppCore import AppCore; app = AppCore.AppCore(); app.restart_application()"], capture_output=True)
        assert proc.returncode == 1

if __name__ == "__main__":
    pytest.main([__file__])