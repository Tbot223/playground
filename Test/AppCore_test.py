# external modules
from pathlib import Path
import pytest
import sys
import os

# internal modules
from Core import AppCore


@pytest.fixture(scope="module")
def setup_module():
    core = AppCore.AppCore()
    file_manager = AppCore.FileManager()
    exception_tracker = AppCore.ExceptionTracker()
    return core, file_manager, exception_tracker

@pytest.mark.usefixtures("tmp_path", "setup_module")
class TestAppCore:
    def test_find_keys_by_value(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        def comparison_func(result, comparison_type):
            excepted = { "above": ["c"], "below": ["a"], "equal": ["b"] }
            assert set(result) == set(excepted[comparison_type])

        # Basic test case - integer comparison
        for comparison_type in ["above", "below", "equal"]:
            result = core.find_keys_by_value({"a": 1, "b": 2, "c": 3}, 2, comparison_type)
            assert result.success
            comparison_func(result.data, comparison_type)
        # Additional test case - string comparison
        for comparison_type in ["above", "below", "equal"]:
            result = core.find_keys_by_value({"a": "apple", "b": "banana", "c": "cherry"}, "banana", comparison_type)
            assert result.success
            comparison_func(result.data, comparison_type)
        # Additional test case - floating point comparison
        for comparison_type in ["above", "below", "equal"]:
            result = core.find_keys_by_value({"a": 0.1, "b": 0.2, "c": 0.3}, 0.2, comparison_type)
            assert result.success
            comparison_func(result.data, comparison_type)

    def test_find_keys_by_value_invalid_type(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        result = core.find_keys_by_value({"a": 1, "b": 2}, [1,2], "equal")
        assert not result.success
        assert "is not supported." in result.error

    def test_getTextByLang(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module
        
        result = core.getTextByLang("en", "Test Key")
        assert result.success
        assert result.data == "This is a test value"

    def test_Atomic_write(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        test_file = tmp_path / "test.txt"
        result = file_manager.Atomic_write("Sample Content", test_file)
        assert result.success
        assert test_file.exists()
        assert test_file.read_text() == "Sample Content"
        file_manager.Atomic_write("Updated Content", test_file)
        assert test_file.read_text() == "Updated Content"

    def test_load_file(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        test_file = tmp_path / "test.txt"
        test_file.write_text("Sample Content")
        result = file_manager.load_file(test_file)
        assert result.success
        assert result.data == "Sample Content"

    def test_save_json(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        test_file = tmp_path / "test.json"
        data = {
            "key": "value",
            "jone": {
                "age": 30,
                "city": "New York"
            },
            "list": [1, 2, 3, 4, 5]
        }
        result = file_manager.save_json(data, test_file)
        assert result.success
        assert test_file.read_text() == '{"key": "value", "jone": {"age": 30, "city": "New York"}, "list": [1, 2, 3, 4, 5]}'

        # Single object save (update) test
        data_update = {
            "age": 31,
            "city": "Los Angeles"
        }
        result = file_manager.save_json(data_update, test_file, key="jone")
        assert result.success
        assert test_file.read_text() == '{"key": "value", "jone": {"age": 31, "city": "Los Angeles"}, "list": [1, 2, 3, 4, 5]}'

    def test_load_json(self, tmp_path, setup_module):
        core, file_manager, exception_tracker = setup_module

        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value", "jone": {"age": 30, "city": "New York"}, "list": [1, 2, 3, 4, 5]}')
        result = file_manager.load_json(test_file)
        assert result.success
        assert result.data == {
            "key": "value",
            "jone": {
                "age": 30,
                "city": "New York"
            },
            "list": [1, 2, 3, 4, 5]
        }

    def test_get_exception_location(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        try:
            1 / 0
        except Exception as e:
            result = exception_tracker.get_exception_location(e)
            assert result.success
            assert result.error == None

    def test_get_exception_info(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        try:
            1 / 0
        except Exception as e:
            result = exception_tracker.get_exception_info(e)
            assert result.success
            assert "ZeroDivisionError" == result.data['error']['type']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])