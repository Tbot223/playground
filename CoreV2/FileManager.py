#external Modules
import os
from typing import List, Union, Any, Dict, Tuple
from pathlib import Path
import tempfile
import json
import shutil
import stat

#internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker
from CoreV2 import Utils, LogSys

class FileManager:
    """
    """

    def __init__(self, is_logging_enabled: bool=True, is_debug_enabled: bool=False,
                 base_dir: Union[str, Path]=None,
                 logger_manager_instance: LogSys.LoggerManager=None, logger: Any=None, log_instance: LogSys.Log=None, Utils_instance: Utils.Utils=None):
        
        # Initialize paths
        self._BASE_DIR = base_dir or Path(__file__).resolve().parent.parent

        # Initialize Flags
        self.is_logging_enabled = is_logging_enabled
        self.is_debug_enabled = is_debug_enabled

        # Initialize classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self.logger = None
        if self.is_logging_enabled:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="file_manager")
            self._logger_manager.make_logger("FileManagerLogger")
            self.logger = logger or self._logger_manager.get_logger("FileManagerLogger")
        self.log = log_instance or LogSys.Log(logger=self.logger)
        self._utils = Utils_instance or Utils.Utils()

        self.log.log_message("INFO", "FileManager initialized.")

    # internal Methods
    @staticmethod
    def _handle_exc(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def _str_to_path(self, path: Any) -> Path:
        """
        Convert string path to Path object
        """
        return self._utils.str_to_path(path)
            

    def atomic_write(self, file_path: Union[str, Path], data: Any) -> Result:
        """
        Atomically write "data" to "file_path"

        - If data is bytes, write in binary mode; if str, write in text mode with utf-8 encoding.
        - Use a temporary file in the same directory and rename it to ensure atomicity.
        - Ensure that the parent directory of file_path exists; create it if it does not.
        - Flush and sync data to disk before renaming to minimize data loss risk.
        """
        try:
            temp_path = None
            file_path = self._str_to_path(file_path)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            is_bytes = isinstance(data, bytes)
            mode = 'wb' if is_bytes else 'w'
            encoding = None if is_bytes else 'utf-8'

            with tempfile.NamedTemporaryFile(mode, delete=False, dir=str(file_path.parent), encoding=encoding) as temp:
                temp_path = Path(temp.name)
                temp.write(data)
                temp.flush()
                try:
                    os.fsync(temp.fileno())
                except (AttributeError, OSError):
                    pass  # os.fsync not available on some platforms

            os.replace(temp_path, file_path)
            return Result(True, None, None, f"Successfully wrote to {file_path}")
                
        except Exception as e:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception:
                pass
            return self._exception_tracker.get_exception_return(e)
        
    def read_file(self, file_path: Union[str, Path], as_bytes: bool=False) -> Result:
        """
        Read the content of the file at "file_path"

        - If as_bytes is True, read in binary mode; otherwise, read in text mode with utf-8 encoding.
        - Return the content in the data field of the Result object.
        """
        try:
            file_path = self._str_to_path(file_path)

            mode = 'rb' if as_bytes else 'r'
            encoding = None if as_bytes else 'utf-8'

            with open(file_path, mode, encoding=encoding) as f:
                content = f.read()
            return Result(True, None, None, content)

        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def write_json(self, file_path: Union[str, Path], data: Any, indent: int=4) -> Result:
        """
        Write JSON serializable "data" to "file_path" in JSON format

        - Use atomic_write to ensure atomicity.
        - Pretty-print JSON with specified indentation.
        """
        try:
            file_path = self._str_to_path(file_path)
            json_data = json.dumps(data, indent=indent, ensure_ascii=False)
            write_result = self.atomic_write(file_path, json_data)
            if not write_result.success:
                return write_result
            return Result(True, None, None, f"Successfully wrote JSON to {file_path}")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def read_json(self, file_path: Union[str, Path]) -> Result:
        """
        Read JSON content from "file_path" and parse it into a Python object

        - Return the parsed object in the data field of the Result object.
        """
        try:
            file_path = self._str_to_path(file_path)
            if file_path.exists() is False:
                raise FileNotFoundError(f"File not found: {file_path}")
            if file_path.suffix.lower() != '.json':
                raise ValueError("File extension is not .json")

            read_result = self.read_file(file_path, as_bytes=False)
            if not read_result.success:
                return read_result
            return Result(True, None, None, read_result.data)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def list_of_files(self, dir_path: Union[str, Path], extensions: List[str]=None, only_name: bool = False) -> Result:
        """
        List all files in the directory at "dir_path"

        - If "extension" is provided, filter files by the given extension (case-insensitive).
        - Return the list of file paths in the data field of the Result object.
        - If only_name is True, return only file names instead of full paths.
        """
        try:
            dir_path = self._str_to_path(dir_path)
            extensions = [ext.lower() for ext in extensions] if extensions is not None else []

            if not dir_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")

            def is_matching_file(item: Path) -> str:
                if os.path.isfile(item):
                    return
                if extensions is None or item.suffix.lower() in extensions:
                    return item.stem if only_name else str(item)

            files = []
            for item in dir_path.iterdir():
                files.append(is_matching_file(item))

            return Result(True, None, None, files)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def delete_file(self, file_path: Union[str, Path]) -> Result:
        """
        Delete the file at "file_path"
        """
        try:
            file_path = self._str_to_path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            try:
                file_path.unlink()
            except PermissionError:
                os.chmod(file_path, stat.S_IWRITE)
                file_path.unlink()

            return Result(True, None, None, f"Successfully deleted {file_path}")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def delete_directory(self, dir_path: Union[str, Path]) -> Result:
        """
        Delete the directory at "dir_path" and all its contents
        """
        try:
            dir_path = self._str_to_path(dir_path)
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {dir_path}")
            if not dir_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")

            try:
                shutil.rmtree(dir_path)
            except PermissionError:
                shutil.rmtree(dir_path, onexc=self._handle_exc)

            return Result(True, None, None, f"Successfully deleted directory {dir_path}")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def create_directory(self, dir_path: Union[str, Path]) -> Result:
        """
        Create the directory at "dir_path"

        - If the directory already exists, do nothing.
        """
        try:
            dir_path = self._str_to_path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return Result(True, None, None, f"Successfully created directory {dir_path}")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    # __enter__ and __exit__
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass