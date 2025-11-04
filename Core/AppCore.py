# external modules
import os
import subprocess
from typing import Any, Dict, List, Tuple, Union, Optional, Callable
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# internal modules
from Core import Result, DebugTool, FileManager
from Core import LogSys as log
from Core.Exception import ExceptionTracker

# Global Variables

class AppCore:
    """
    The AppCore class provides integrated core system functionality for multiple programs.

    Provides core system functionality applicable to most programs.

    1. Multilingual Support: Provides functionality to manage and return text in multiple languages.
        - getTextByLang: Returns text according to language settings.

    2. Data Structure Search: Provides functionality to find keys that meet specific conditions in dictionaries.
        - find_keys_by_value: Finds keys with values above a specific threshold in dictionaries.

    3. Screen Clearing: Provides platform-independent screen clearing functionality.
        - clear_screen: Clears the screen.
    """

    def __init__(self, screen_clear_lines: int = 50, parent_dir: Union[str, Path] = None, isTest: bool = False, isDebug: bool = False, logger = None, No_Log: bool = False, 
                filemanager: FileManager = None, logger_manager: log.LoggerManager = None, debug_tool: DebugTool.DebugTool = None, log_class: log.Log = None):
        """
        Initialize AppCore

        Dependency Injection available for: - It's not required to inject all these classes, only the ones you want to customize.
        - instance will create default instances if not provided.
            - FileManager : FileManager
            - LoggerManager : log.LoggerManager
            - DebugTool : DebugTool.DebugTool
            - Log : log.Log
        """
        print("Initializing AppCore...")
        # Set directory
        self._PARENT_DIR = parent_dir or Path(__file__).resolve().parent.parent
        if isinstance(self._PARENT_DIR, str):
            self._PARENT_DIR = Path(self._PARENT_DIR)
        self.LANGUAGE_DIR = Path(self._PARENT_DIR / "language")
        self.LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
        os.makedirs(self.LANGUAGE_DIR, exist_ok=True)

        # Initialize Classes

        self._exception_tracker = ExceptionTracker()
        self._LOGGER_MANAGER = logger_manager or log.LoggerManager(base_dir=self.LOG_DIR, second_log_dir="AppCoreLogs")
        self._LOGGER_MANAGER.Make_logger("AppCore")
        self._logger = logger or self._LOGGER_MANAGER.get_logger("AppCore").data
        self._debug_tool = debug_tool or DebugTool.DebugTool(logger=self._logger)
        self._log = log_class or log.Log(logger=self._logger)
        self._file_manager = filemanager or FileManager(logger_manager=self._LOGGER_MANAGER)

        # Set variables
        self.SCREEN_CLEAR_LINES = screen_clear_lines if screen_clear_lines > 0 else 50
        self._LANG = [os.path.splitext(file)[0] for file in os.listdir(self.LANGUAGE_DIR) if file.endswith('.json')]
        self._lang_cache = {}
        self.isTest = isTest
        self.isDebug = isDebug
        self.No_Log = No_Log

        self._logger.info("AppCore initialized successfully.")

    def find_keys_by_value(self, json_data: Dict, threshold: Any, comparison_type: str, nested_lookup: bool = False) -> Result:
        """
        Function to find keys with values above a specific threshold in dictionaries

        For string values, only 'equal' comparison is supported.
        (bit comparison support planned)

        Args:
            comparison_type (str): Comparison type ("above", "below", "equal")
            threshold (Any, But list, dict, tuple is not allowed): Reference value
        """
        try:
            matching_keys = []
            comparison_type = comparison_type.lower()

            if not isinstance(json_data, dict): # Check json_data type
                raise ValueError("json_data must be a dictionary. it is not supported.")
            if isinstance(threshold, (dict, list, tuple)): # Check threshold type
                raise ValueError("Threshold of type dict, list, or tuple is not supported.")
            if comparison_type not in ["above", "below", "equal"]: # Check comparison type
                raise ValueError("Invalid comparison type, comparison_type must be 'above', 'below', or 'equal'.")

            compare_ops = {
                "above": lambda v: v > threshold, # '>' operator
                "below": lambda v: v < threshold, # '<' operator
                "equal": lambda v: v == threshold # '==' operator
            }
            def lookup(data: Dict):
                for key, value in data.items():
                    threshold_is_str = isinstance(threshold, str)
                    value_is_str = isinstance(value, str)
                    if threshold_is_str != value_is_str and comparison_type != "equal":
                        self._debug_tool.debug_log(f"Skipping key '{key}' due to type mismatch for non-equal comparison.", self.isDebug)
                        continue
                    if isinstance(value, (list, tuple)):
                        self._debug_tool.debug_log(f"Skipping key '{key}' because its value is of unsupported type ({type(value).__name__}).", self.isDebug)
                        continue
                    if isinstance(value, dict) and nested_lookup:
                        lookup(value)  # Recursive call for nested dictionary
                        continue
                    elif compare_ops[comparison_type](value): # Perform comparison
                        self._debug_tool.debug_log(f"Key '{key}' matches the condition: {value} {comparison_type} {threshold}.", self.isDebug)
                        matching_keys.append(key)

            lookup(json_data)

            self._log.log_msg("info", f"find_keys_by_value completed.", self.No_Log)
            self._debug_tool.debug_log(f"Matching keys: {matching_keys}", self.isDebug)

            return Result(True, None, None, matching_keys)
        except Exception as e:
            self._log.log_msg("error", f"Error occurred in find_keys_by_value: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def getTextByLang(self, lang: str, key: str) -> Result:
        """
        Function to return text according to language settings

        No fallback mechanism.
        Must verify that language and key are valid before calling.
        Cache initialization and exception handling on failure.
        """
        try:
            if lang not in self._LANG: # Check language
                raise ValueError(f"Language '{lang}' is not supported. Available languages: {self._LANG}")

            # Check cache
            if lang not in self._lang_cache:
                cache = self._file_manager.load_json(f"{self._PARENT_DIR}/language/{lang}.json")
                if not cache.success:
                    raise FileNotFoundError(f"Language file for '{lang}' could not be loaded.")
                self._lang_cache[lang] = cache.data

            # Return text
            if key in self._lang_cache[lang]:
                return Result(True, None, None, self._lang_cache[lang][key])
            else:
                raise KeyError(f"Key '{key}' not found in language '{lang}'. Available keys: {list(self._lang_cache[lang].keys())}")
        except Exception as e:
            self._lang_cache.pop(lang, None)  # Clear cache on error
            self._log.log_msg("error", f"Error occurred in getTextByLang: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def clear_screen(self):
        """
        Function to clear the screen
        Uses platform-independent and safe methods.

        - Returns is not necessary as this function does not return any value.
        - This function clears the console screen.
        """
        try:
            if os.name == 'nt':  # Windows
                subprocess.run('cls', shell=True, check=True)
            else:  # Unix/Linux/macOS
                subprocess.run('clear', shell=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Alternative when command execution fails
            print('\n' * self.SCREEN_CLEAR_LINES)

    def multi_process_executer(self, tasks: List[Tuple[Callable, Dict]], process: int = 2, overprocess: bool = False) -> Result:
        """
        Function to execute multiple tasks in parallel using multiprocessing

        Args:
            tasks (List[Tuple[Callable, Dict]]): List of tuples containing function and its keyword arguments
                - Each tuple: (function, {arg1: value1, arg2: value2, ...})
                - function: Callable function to execute
                - Dict: Dictionary of keyword arguments for the function ( It must be keyword arguments only. Positional arguments are not supported. )
            process (int): Number of processes to use

        Returns:
            Result: Result object containing list of Result objects for each task ( It is guaranteed that the order of results matches the order of tasks. )
                - example: ( WARNING: The result data is a list of Result objects. )
                - [Result(True, None, None, result1), Result(False, "Error message", "Error location", "Error info"), ...]
        """
        if process < 1 or not isinstance(process, int):
            self._log.log_msg("warning", f"Invalid process count ({process}). Defaulting to 2 processes.", self.No_Log)
            process = 2  # Default to 2 processes if invalid
        if process > len(tasks) and not overprocess:
            self._log.log_msg("warning", f"Requested process count ({process}) exceeds number of tasks ({len(tasks)}). Adjusting process count to match number of tasks.", self.No_Log)
            process = len(tasks)  # Limit to number of task
        if len(tasks) == 0:
            self._log.log_msg("warning", "No tasks to execute in multi_process_executer.", self.No_Log)
            return Result(True, None, None, [])  # No tasks to execute
        if not isinstance(tasks, list):
            self._log.log_msg("error", "Tasks must be provided as a list of tuples in multi_process_executer.", self.No_Log)
            return Result(False, "Tasks must be provided as a list of tuples.", None, None)
        if not all(isinstance(t, tuple) and len(t) == 2 and callable(t[0]) and isinstance(t[1], dict) for t in tasks):
            self._log.log_msg("error", "Each task must be a tuple of (callable, kwargs_dict) in multi_process_executer.", self.No_Log)
            return Result(False, "Each task must be a tuple of (callable, kwargs_dict).", None, None)

        try:
            process = min(process, os.cpu_count() * 4)  # Limit process to 4 times CPU count
            results = [None] * len(tasks)
            with ProcessPoolExecutor(max_workers=process) as executor:
                future_to_index = {executor.submit(func, **kwargs): idx for idx, (func, kwargs) in enumerate(tasks)}
                
                for future in as_completed(future_to_index):
                    idx = future_to_index[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        self._log.log_msg("error", f"Error in task {idx}: {str(e)}", self.No_Log)
                        results[idx] = Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
                        
            self._log.log_msg("info", "multi_process_executer completed successfully.", self.No_Log)
            return Result(True, None, None, results)
        except Exception as e:
            self._log.log_msg("error", f"Error occurred in multi_process_executer: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)