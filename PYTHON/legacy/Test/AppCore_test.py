# external modules
from pathlib import Path
import pytest
import sys
import os

# internal modules
from Core import AppCore, FileManager
from Core import LogSys as log
from Core import ExceptionTracker


@pytest.fixture(scope="module")
def setup_module():
    log_manager = log.LoggerManager(second_log_dir="TestLogs")
    file_manager = FileManager(logger_manager=log_manager)
    core = AppCore.AppCore(logger_manager=log_manager, filemanager=file_manager)
    exception_tracker = ExceptionTracker()
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

    def test_batch_process_json_threaded(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Create multiple JSON files
        files = []
        for i in range(5):
            file_path = tmp_path / f"test_{i}.json"
            file_manager.save_json({"key": f"value_{i}"}, file_path)
            files.append(file_path)

        result = file_manager.load_json_threaded(files)
        assert result.success

        # Verify each file has been processed
        for i in range(5):
            file = tmp_path / f"test_{i}.json"
            content = file.read_text()
            assert content == f'{{"key": "value_{i}"}}'

    def test_batch_process_write_json_threaded(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        data_list = []
        for i in range(5):
            file = tmp_path / f"data_{i}.json"
            data = {"new_key": f"value_{i}"}
            data_list.append((data, file, False))
            
        result = file_manager.write_json_threaded(data_list)
        assert result.success

        # Verify each file has been created and processed
        for i in range(5):
            file = tmp_path / f"data_{i}.json"
            assert file.exists()
            content = file.read_text()
            assert content == '{"new_key": "value_' + str(i) + '"}'

class TestEdgeCases:
    def test_find_keys_by_value_invalid_type(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Invalid type tests
        result = core.find_keys_by_value({"a": 1, "b": 2}, [1,2], "equal")
        assert not result.success
        assert "is not supported." in result.error
        # Invalid json_data type
        result = core.find_keys_by_value([1,2,3], 2, "equal")
        assert not result.success
        assert "is not supported." in result.error
        # Invalid comparison_type
        result = core.find_keys_by_value({"a": 1, "b": 2}, 2, "invalid_type")
        assert not result.success
        assert "Invalid comparison type" in result.error

    def test_getTextByLang_not_supported_language(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        result = core.getTextByLang("fr", "Test Key")
        assert not result.success
        assert "Language 'fr' is not supported." in result.error
    
    def test_getTextByLang_cannot_load_json(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Simulate crashed JSON file by creating an invalid JSON file
        json_file = tmp_path / "fr.json"
        json_file.write_text('{"Test Key": "This is a test value"')  # Missing closing brace
        core._LANG.append("fr")  # Add 'fr' to supported languages
        result = core.getTextByLang("fr", "Test Key")
        assert not result.success
        assert "Language file for 'fr' could not be loaded." in result.error

        file_manager._PARENT_DIR = core._PARENT_DIR  # Restore original path
        core._LANG.pop()  # Remove 'fr' from supported languages

    def test_key_not_found(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Key not found test
        result = core.getTextByLang("en", "Nonexistent Key")
        assert not result.success
        assert "Key 'Nonexistent Key' not found in language 'en'." in result.error

    def test_save_json_cannot_load_existing_json(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        save_path = tmp_path / "test.json"
        result = file_manager.save_json({"key": "value"}, save_path, "Test Key")  # Initial save
        assert not result.success
        assert "Failed to load existing JSON file:" in result.error

    def test_batch_process_json_threaded_with_invalid_files(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Invalid files list (not strings)
        files = [123, None, 12.34]
        result = file_manager.load_json_threaded(files)
        assert not result.success
        assert "file_paths must be a list of strings or Path objects." in result.error

        # Empty files list
        result = file_manager.load_json_threaded([])
        assert not result.success
        assert "file_paths list is empty or None." in result.error

    def test_batch_process_write_json_threaded_with_invalid_data_list(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Invalid data_list structure
        data_list = [("not_a_dict", tmp_path / "file1.json", False), ({"key": "value"}, 123, True)]
        result = file_manager.write_json_threaded(data_list)
        assert not result.success
        assert "data_list must be a list of tuples in the form (dict, str, bool)." in result.error

        # Empty data_list
        result = file_manager.write_json_threaded([])
        assert not result.success
        assert "data_list is empty or None." in result.error


    def test_Atomic_write_with_invalid_path(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Invalid path (e.g., directory instead of file)
        result = file_manager.Atomic_write("Content", 0.42)
        assert not result.success
        assert "TypeError" in result.error

    def test_Atomic_write_with_empty_data(self, tmp_path: Path, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        test_file = tmp_path / "test.txt"
        result = file_manager.Atomic_write("", test_file)
        assert not result.success
        assert "Data to write is empty or None." in result.error

    def test_find_keys_by_value_threshold_type(self, setup_module: tuple):
        core, file_manager, exception_tracker = setup_module

        # Threshold as string
        result = core.find_keys_by_value({"a": 1, "b": 2, "c": (2, 3), "d": {"a": 1}, "e":[2, 3]}, "2", "equal")
        assert result.success
        assert result.data == []
        
        # Value type mismatch
        result = core.find_keys_by_value({"a": 1, "b": "2", "c": 3}, 2.0, "equal")
        assert result.success
        assert result.data == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])