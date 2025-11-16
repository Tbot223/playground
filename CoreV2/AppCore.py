#external Modules
import os
import subprocess
import sys
from typing import Any, Callable, List, Dict, Tuple, Union, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor, as_completed as pc_as_completed

#internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker
from CoreV2 import FileManager, LogSys

class AppCore:
    """
    Placeholder class for AppCore in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self, is_logging_enabled: bool=True, is_debug_enabled: bool=False,
                 base_dir: Union[str, Path]=None,
                 logger_manager_instance: LogSys.LoggerManager=None, logger: Any=None, log_instance: LogSys.Log=None,
                 filemanager: FileManager.FileManager=None):

        # Initialize paths
        self._PARENT_DIR = base_dir or Path(__file__).resolve().parent.parent
        self._LANG_DIR = self._PARENT_DIR / "Languages"    

        # Initialize Flags
        self.is_logging_enabled = is_logging_enabled
        self.is_debug_enabled = is_debug_enabled
        # Initialize classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self.logger = None
        if self.is_logging_enabled:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._PARENT_DIR / "logs", second_log_dir="app_core")
            self._logger_manager.make_logger("AppCoreLogger")
            self.logger = logger or self._logger_manager.get_logger("AppCoreLogger")
        self.log = log_instance or LogSys.Log(logger=self.logger)
        self._file_manager  = filemanager or FileManager.FileManager(is_logging_enabled=False, base_dir=self._PARENT_DIR)
        
        # Initialize internal variables
        self._lang_cache = {}
        self._default_lang = "en"
        self._supported_langs = self._file_manager.list_of_files(self._LANG_DIR, extensions=['.json'], only_name=True).data

        self.log.log_message("INFO", f"AppCore initialized. Supported languages: {self._supported_langs}")
    
    # internal Methods
    @staticmethod
    def _check_executable(data: List[Tuple[Callable[ ... , Any], Dict]], workers: int, override: bool, timeout: float) -> Union[bool, str]:
        """
        Check if the functions in data and workers are valid for execution.
        """
        if not isinstance(data, list) or len(data) == 0:
            return False, "Data must be a non-empty list"
        for item in data:
            if not (isinstance(item, tuple) and len(item) == 2 and callable(item[0]) and isinstance(item[1], dict)):
                return False, "Each item in data must be a tuple of (callable, dict)"
        if workers is not None and (not isinstance(workers, int) or workers <= 0):
            return False, "workers must be a positive integer"
        if workers > len(data) and not override:
            return False, f"workers {workers} exceeds number of tasks {len(data)}"
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0.1):
            return False, "timeout must be a positive number"
        return True
    
    def _generic_executor(self, data: List[Tuple[Callable[ ... , Any], Dict]], workers: int, timeout: float, type: str) -> List[Result]:
        """
        Generic executor method to be used by both thread and process pool executors.
        """
        results = [None] * len(data)

        executor_type = ThreadPoolExecutor if type == 'thread' else ProcessPoolExecutor
        let_as_completed = as_completed if type == 'thread' else pc_as_completed
        with executor_type(workers=workers) as executor:
            future_to_task = {executor.submit(func, **params): idx for idx, (func, params) in enumerate(data)}

            results = [None] * len(data)
            for future in let_as_completed(future_to_task):
                idx = future_to_task[future]
                try:
                    result = future.result(timeout=timeout)
                    results[idx] = Result(True, None, None, result)
                except Exception as e:
                    results[idx] = self._exception_tracker.get_exception_return(e, params=data[idx][1])
        return results
    
    def _lookup_dict(self, dict_obj: Dict, threshold: Union[int, float, str, bool], comparison_func: Callable, comparison_type: str, nested: bool) -> List:
        """
        Helper method to recursively look up keys in a dictionary based on a comparison function.
        """
        found_keys = []
        for key, value in dict_obj.items():
            if isinstance(value, (str, bool)) == isinstance(threshold, str, bool) and comparison_type in ['eq', 'ne']:
                if comparison_func(value):
                    found_keys.append(key)
            if isinstance(value, (tuple, list)):
                continue
            if comparison_func(value):
                found_keys.append(key)
            if nested and isinstance(value, dict):
                found_keys.append(self._lookup_dict(value, threshold, comparison_func, comparison_type, nested))
        return found_keys

    # external Methods
    def thread_pool_executor(self, data: List[Tuple[Callable[ ... , Any], Dict]], workers: int = None, override: bool = False, timeout: float = None) -> Result:
        """
        Execute functions in parallel using ThreadPoolExecutor.
        """
        try:
            is_valid, error_message = self._check_executable(data, workers, override, timeout)
            if not is_valid:
                return Result(False, error_message, None, None)
            workers = min(workers or os.cpu_count() * 2, os.cpu_count() * 2)
            results = self._generic_executor(data, workers, timeout, type='thread')

            return Result(True, None, None, results)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

    def process_pool_executor(self, data: List[Tuple[Callable[ ... , Any], Dict]], workers: int = None, override: bool = False, timeout: float = None) -> Result:
        """
        Execute functions in parallel using ProcessPoolExecutor.
        """
        try:
            is_valid, error_message = self._check_executable(data, workers, override, timeout)
            if not is_valid:
                return Result(False, error_message, None, None)
            workers = min(workers or os.cpu_count() * 2, os.cpu_count() * 2)
            results = self._generic_executor(data, workers, timeout, type='process')

            return Result(True, None, None, results)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

    def find_keys_by_value(self, dict_obj: Dict, threshold: Union[int, float, str, bool],  comparison: str='eq', nested: bool=False) -> Result:
        """
        Find keys in dict_obj where their values meet the threshold based on the comparison operator.

        [bool, str] - [int, float] comparisons are only supported for 'eq' and 'ne'.

        Supported comparison operators:
        - 'eq': equal to
        - 'ne': not equal to
        - 'lt': less than
        - 'le': less than or equal to
        - 'gt': greater than
        - 'ge': greater than or equal to
        """
        comparison_operators = {
            'eq': lambda x: x == threshold,
            'ne': lambda x: x != threshold,
            'lt': lambda x: x < threshold,
            'le': lambda x: x <= threshold,
            'gt': lambda x: x > threshold,
            'ge': lambda x: x >= threshold,
        }

        try:
            if comparison not in comparison_operators:
                raise ValueError(f"Unsupported comparison operator: {comparison}")
            if isinstance(dict_obj, dict) is False:
                raise ValueError("Input is not a dictionary")
            if isinstance(threshold, (str, bool, int, float)) is False:
                raise ValueError("Threshold must be of type str, bool, int, or float")
            
            comparison_func = comparison_operators[comparison]
            found_keys = self._lookup_dict(dict_obj, threshold, comparison_func, comparison, nested)

            return Result(True, None, None, found_keys)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def get_text_by_lang(self, key: str, lang: str) -> Result:
        """
        Retrieve localized text for the given key and language.

        - If the key does not exist in the language file, return an error.
        """

        try:
            if lang not in self._supported_langs:
                lang = self._default_lang

            if lang not in self._lang_cache:
                lang_file_path = self._LANG_DIR / f"{lang}.json"
                read_result = self._file_manager.read_json(lang_file_path)
                if not read_result.success:
                    return read_result
                self._lang_cache[lang] = read_result.data

            if key not in self._lang_cache[lang]:
                return Result(False, f"Key '{key}' not found in language '{lang}'", None, None)
            
            return Result(True, None, None, self._lang_cache[lang][key])

        except Exception as e:
            self._lang_cache.pop(lang)
            return self._exception_tracker.get_exception_return(e)
        
    def clear_console(self) -> Result:
        """
        Clear the console screen using the appropriate command based on the operating system.
        """
        try:
            command = 'cls' if os.name == 'nt' else 'clear'
            subprocess.run(command, shell=True, check=True)
            return Result(True, None, None, "Console cleared successfully.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def exit_application(self, code: int=0) -> Result:
        """
        Exit the application with the specified exit code.
        """
        try:
            os._exit(code)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
    def restart_application(self) -> Result:
        """
        Restart the current application.
        """
        try:
            python = sys.executable
            os.execl(python, python, * sys.argv)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)