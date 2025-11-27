# external Modules
import pytest

# internal Modules
from CoreV2 import FileManager

@pytest.fixture(scope="module")
def file_manager():
    """
    Fixture to create a FileManager instance for testing.
    """
    return FileManager.FileManager()

@pytest.mark.usefixtures("tmp_path", "file_manager")
class TestFileManager:
    def test_atomic_write_and_read(self, file_manager, tmp_path):
        test_file = tmp_path / "test_atomic.txt"
        test_data = "This is a test string for atomic write and read."

        # Test atomic write
        write_result = file_manager.atomic_write(file_path=test_file, data=test_data)
        assert write_result.success, f"Atomic write failed: {write_result.error}"

        # Test atomic read
        read_result = file_manager.read_file(file_path=test_file, as_bytes=False)
        assert read_result.success, f"Atomic read failed: {read_result.error}"
        assert read_result.data == test_data, "Data read does not match data written."

        # Test atomic write in bytes mode
        test_data_bytes = b"This is a test byte string for atomic write and read."
        write_result_bytes = file_manager.atomic_write(file_path=test_file, data=test_data_bytes)
        assert write_result_bytes.success, f"Atomic write (bytes) failed: {write_result_bytes.error}"

        # Test atomic read in bytes mode
        read_result_bytes = file_manager.read_file(file_path=test_file, as_bytes=True)
        assert read_result_bytes.success, f"Atomic read (bytes) failed: {read_result_bytes.error}"
        assert read_result_bytes.data == test_data_bytes, "Byte data read does not match byte data written."

    def test_write_json_and_read_json(self, file_manager, tmp_path):
        test_file = tmp_path / "test_data.json"
        test_data = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}

        # Test write JSON
        write_result = file_manager.write_json(file_path=test_file, data=test_data)
        assert write_result.success, f"Write JSON failed: {write_result.error}"

        # Test read JSON
        read_result = file_manager.read_json(file_path=test_file)
        assert read_result.success, f"Read JSON failed: {read_result.error}"
        assert read_result.data == test_data, "JSON data read does not match data written."

    def test_list_of_files(self, file_manager, tmp_path):
        # Create test files
        (tmp_path / "file1.txt").write_text("File 1")
        (tmp_path / "file2.log").write_text("File 2")
        (tmp_path / "file3.txt").write_text("File 3")

        # Test listing .txt files
        list_result = file_manager.list_of_files(dir_path=tmp_path, extensions=[".txt"], only_name=True)
        assert list_result.success, f"List of files failed: {list_result.error}"
        expected_files = {"file1", "file3"}
        assert set(list_result.data) == expected_files, "Listed files do not match expected files."

        #Test No extension filter and full paths
        list_result_all = file_manager.list_of_files(dir_path=tmp_path, extensions=[], only_name=False)
        assert list_result_all.success, f"List of files failed: {list_result_all.error}"
        expected_files_all = {str(tmp_path / "file1.txt"), str(tmp_path / "file2.log"), str(tmp_path / "file3.txt")}
        assert set(list_result_all.data) == expected_files_all, "Listed files do not match expected files."

    def test_delete_file(self, file_manager, tmp_path):
        test_file = tmp_path / "test_delete.txt"
        test_file.write_text("This file will be deleted.")

        # Ensure file exists
        assert test_file.exists(), "Test file does not exist before deletion."

        # Test delete file
        delete_result = file_manager.delete_file(file_path=test_file)
        assert delete_result.success, f"Delete file failed: {delete_result.error}"

        # Ensure file is deleted
        assert not test_file.exists(), "Test file still exists after deletion."

    def test_delete_directory(self, file_manager, tmp_path):
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("File 1")
        (test_dir / "file2.txt").write_text("File 2")

        # Ensure directory exists
        assert test_dir.exists() and test_dir.is_dir(), "Test directory does not exist before deletion."

        # Test delete directory
        delete_result = file_manager.delete_directory(dir_path=test_dir)
        assert delete_result.success, f"Delete directory failed: {delete_result.error}"

        # Ensure directory is deleted
        assert not test_dir.exists(), "Test directory still exists after deletion."

    def create_directory(self, file_manager, tmp_path):
        test_dir = tmp_path / "new_test_dir"

        # Test create directory
        create_result = file_manager.create_directory(dir_path=test_dir)
        assert create_result.success, f"Create directory failed: {create_result.error}"

        # Ensure directory is created
        assert test_dir.exists() and test_dir.is_dir(), "Test directory was not created."

    def test_exist(self, file_manager, tmp_path):
        test_file = tmp_path / "test_exist.txt"
        test_file.write_text("This file is for existence check.")

        # Test exist for existing file
        exist_result = file_manager.exist(path=test_file)
        assert exist_result.success, f"Exist check failed: {exist_result.error}"
        assert exist_result.data is True, "Exist check returned False for existing file."

        # Test exist for non-existing file
        non_exist_file = tmp_path / "non_existing.txt"
        exist_result_non = file_manager.exist(path=non_exist_file)
        assert exist_result_non.success, f"Exist check failed: {exist_result_non.error}"
        assert exist_result_non.data is False, "Exist check returned True for non-existing file."

    def test_with_exit(self, file_manager, tmp_path):
        test_file = tmp_path / "test_with.txt"
        test_data = "This is a test string for with context manager."

        # Use FileManager as a context manager to write to a file
        with file_manager as fm:
            write_result = fm.atomic_write(file_path=test_file, data=test_data)
            assert write_result.success, f"Atomic write in context manager failed: {write_result.error}"

        # Use FileManager as a context manager to read from the file
        with file_manager as fm:
            read_result = fm.read_file(file_path=test_file, as_bytes=False)
            assert read_result.success, f"Atomic read in context manager failed: {read_result.error}"
            assert read_result.data == test_data, "Data read in context manager does not match data written."

@pytest.mark.usefixtures("tmp_path", "file_manager")
class TestFileManagerXfails:
    def test_read_nonexistent_file(self, file_manager, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.txt"

        # Test reading a non-existent file
        read_result = file_manager.read_file(file_path=nonexistent_file, as_bytes=False)
        assert not read_result.success, "Read operation unexpectedly succeeded for a non-existent file."
        assert read_result.data["error"]["type"] == "FileNotFoundError", "Error is not FileNotFoundError for non-existent file."

class TestFileManagerEdgeCases:
    pass # Placeholder for future edge case tests

if __name__ == "__main__":
    pytest.main([__file__, "-vv"])