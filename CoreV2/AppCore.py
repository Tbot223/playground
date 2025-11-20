#external Modules
import os
import subprocess
import sys
from typing import Any, Callable, List, Dict, Tuple, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor, as_completed as pc_as_completed

#internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker
from CoreV2 import FileManager, LogSys

class AppCore:
    """
    Provides core functionalities for application management.

    This class includes support for multi-threading, localization, console management,
    and dictionary key-value searching. It also integrates logging and file management
    utilities.

    Attributes:
        is_logging_enabled (bool): Flag to enable or disable logging.
        is_debug_enabled (bool): Flag to enable or disable debug mode.
        default_lang (str): Default language code for localization. (Fallback language)
        base_dir (Union[str, Path]): Base directory for the application.
        logger_manager_instance (LogSys.LoggerManager): Instance of LoggerManager for logging.
        logger (Any): Logger instance for logging messages.
        log_instance (LogSys.Log): Instance of Log for logging messages.
        filemanager (FileManager.FileManager): Instance of FileManager for file operations.

    Methods:
        thread_pool_executor(data, workers, override, timeout) -> Result:
            Execute functions in parallel using ThreadPoolExecutor.

        process_pool_executor(data, workers, override, timeout) -> Result:
            Execute functions in parallel using ProcessPoolExecutor.

        find_keys_by_value(dict_obj, threshold, comparison, nested) -> Result:
            Find keys in a dictionary based on value comparisons.
        
        get_text_by_lang(key, lang) -> Result:
            Retrieve localized text for the given key and language.

        clear_console() -> Result:
            Clear the console screen.

        exit_application(code) -> Result:
            Exit the application with the specified exit code. ( Returns Only On Failure )

        restart_application() -> Result:
            Restart the current application. ( Returns Only On Failure )
    """
    
    def __init__(self, is_logging_enabled: bool=True, is_debug_enabled: bool=False, default_lang: str="en",
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
        self._default_lang = default_lang
        self._supported_langs = self._file_manager.list_of_files(self._LANG_DIR, extensions=['.json'], only_name=True).data

        self.log.log_message("INFO", f"AppCore initialized. Supported languages: {self._supported_langs}")
    
    # internal Methods
    @staticmethod
    def _check_executable(data: List[Tuple[Callable[ ... , Any], Dict]], workers: int, override: bool, timeout: float) -> Union[bool, str]:
        """
        Check if the functions in data and workers are valid for execution.
        
        Args:
            data : List of tuples containing functions and their parameters.
            workers : Number of worker threads/processes.
            override : If True, allows workers to exceed the number of tasks.
            timeout : Maximum time to wait for each function to complete.

        Returns:
            Tuple (is_valid: bool, error_message: str)

        Example:
            >> # I'm not recommending to call this method directly, it's for internal use.
            >> data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
            >> is_valid, error_message = app_core._check_executable(data, workers=4, override=False, timeout=10)
            >> if not is_valid:
            >>     print(error_message)
            >> else:
            >>     print("Data and workers are valid for execution.")
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

        Args:
            data : List of tuples containing functions and their parameters.
            workers : Number of worker threads/processes.
            timeout : Maximum time to wait for each function to complete.
            type : 'thread' for ThreadPoolExecutor, 'process' for ProcessPoolExecutor.

        Returns:
            indexed list of Result objects corresponding to each function execution.

        Example:
            >> # I'm not recommending to call this method directly, it's for internal use.
            >> data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
            >> results = app_core._generic_executor(data, workers=4, timeout=10, type='thread')
            >> for res in results:
            >>     print(res.success, res.data)
        """
        results = [None] * len(data)

        executor_type = ThreadPoolExecutor if type == 'thread' else ProcessPoolExecutor
        let_as_completed = as_completed if type == 'thread' else pc_as_completed
        with executor_type(workers=workers) as executor:
            future_to_task = {executor.submit(func, **params): idx for idx, (func, params) in enumerate(data)}
            
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

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison_func : A callable that takes a value and returns True if it meets the condition.
            comparison_type : The type of comparison being performed.
            nested : If True, search within nested dictionaries.

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >> # I'm not recommending to call this method directly, it's for internal use.
            >> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >> found_keys = app_core._lookup_dict(my_dict, threshold=20, comparison_func=lambda x: x > 20, comparison_type='gt', nested=False)
            >> print(found_keys)  # Output: ['c']
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

        Args:
            data : 
            workers : Number of worker threads to use. Defaults to os.cpu_count() * 2.
            override : If True, allows workers to exceed the number of tasks.
            timeout : Maximum time to wait for each function to complete.

        Returns:
            indexed list of Result objects corresponding to each function execution.

        Example:
            >> data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
            >> result = app_core.thread_pool_executor(data, workers=4, override=False, timeout=10)
            >> for res in result.data:
            >>     print(res.success, res.data)
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

        Args:
            data : example: [(func1, {'arg1': val1}), (func2
            workers : Number of worker processes to use. Defaults to os.cpu_count() * 2.
            override : If True, allows workers to exceed the number of tasks.
            timeout : Maximum time to wait for each function to complete.

        Returns:
            indexed list of Result objects corresponding to each function execution.

        Example:
            >> data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
            >> result = app_core.process_pool_executor(data, workers=4, override=False, timeout=10)
            >> for res in result.data:
            >>     print(res.success, res.data)
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

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison : The comparison operator as a string. Default is 'eq' (equal).
            nested : If True, search within nested dictionaries.

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >> result = app_core.find_keys_by_value(my_dict, threshold=20, comparison='gt', nested=False)
            >> print(result.data)  # Output: ['c']

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

        Args:
            key : The key for the desired text.
            lang : The language code (e.g., 'en', 'fr').
        
        Returns:
            The localized text corresponding to the key and language.

        Example:
            >> result = app_core.get_text_by_lang('greeting', 'en')
            >> if result.success:
            >>     print(result.data)  # Output: "Hello"
            >> else:
            >>     print(result.error)
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

        Returns:
            Result object indicating success or failure of the operation.

        Example:
            >> result = app_core.clear_console() # then console is cleared
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

        Args:
            code : Exit code to return to the operating system. Default is 0.

        Returns:
            returns only on failure with a Result object indicating the error.

        Example:
            >> result = app_core.exit_application(0) # then application exits with code 0
        """
        try:
            os._exit(code)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
    def restart_application(self) -> Result:
        """
        Restart the current application.

        Returns:
            returns only on failure with a Result object indicating the error.

        Example:
            >> result = app_core.restart_application() # then application restarts
        """
        try:
            python = sys.executable
            os.execl(python, python, * sys.argv)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)