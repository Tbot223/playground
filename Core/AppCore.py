# external modules
import json
import os
import tempfile
import shutil
import subprocess
from typing import Any, Dict, List, Tuple, Union, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from pathlib import Path

# internal modules
from Core import Result, log, DebugTool
from Core.Exception import ExceptionTracker

# Global Variables

class AppCore:
    """
    The AppCore class provides integrated core system functionality for multiple programs.

    Provides core system functionality applicable to most programs, including 
    JSON file management, multilingual support, and data structure search.

    1. Multilingual Support: Provides functionality to manage and return text in multiple languages.
        - text: Returns text according to language settings.

    2. Data Structure Search: Provides functionality to find keys that meet specific conditions in dictionaries.
        - find_keys_by_value: Finds keys with values above a specific threshold in dictionaries.

    3. Screen Clearing: Provides platform-independent screen clearing functionality.
        - clear_screen: Clears the screen.
    """

    def __init__(self, screen_clear_lines: int=50, parent_dir: str=None, isTest: bool=False, isDebug: bool=False, logger = None, No_Log: bool=False):
        """
        Initialize AppCore
        """
        print("Initializing AppCore...")
        # Set directory
        self._PARENT_DIR = parent_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.LANGUAGE_DIR = f"{self._PARENT_DIR}/language"
        self.LOG_DIR = f"{Path(__file__).resolve().parent.parent}/logs"
        os.makedirs(self.LANGUAGE_DIR, exist_ok=True)

        # Initialize Classes

        self._exception_tracker = ExceptionTracker()
        if logger is None:
            print("No logger provided, initializing default LoggerManager.")
            self._LOGGER_MANAGER = log.LoggerManager(base_dir=self.LOG_DIR, second_log_dir="AppCoreLogs")
            self._LOGGER_MANAGER.Make_logger("AppCore")
        self._logger = self._LOGGER_MANAGER.get_logger("AppCore") if logger is None else logger
        self._debug_tool = DebugTool.DebugTool(logger=self._logger)
        self._log = log.Log(logger=self._logger)
        self._FileManager = FileManager()        

        # Set variables
        self.SCREEN_CLEAR_LINES = screen_clear_lines if screen_clear_lines > 0 else 50
        self._LANG = [os.path.splitext(file)[0] for file in os.listdir(self.LANGUAGE_DIR) if file.endswith('.json')]
        self._lang_cache = {}
        self.isTest = isTest
        self.isDebug = isDebug
        self.No_Log = No_Log

        self._logger.info("AppCore initialized successfully.")

    def find_keys_by_value(self, json_data: Dict, threshold: Any, comparison_type: str) -> Result:
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

            for key, value in json_data.items(): # Iterate through dictionary
                threshold_is_str = isinstance(threshold, str)
                value_is_str = isinstance(value, str)
                if threshold_is_str and not value_is_str and comparison_type != "equal":
                    self._debug_tool.debug_log(f"Skipping key '{key}' due to type mismatch between threshold and value.", self.isDebug)
                    continue
                if not threshold_is_str and value_is_str and comparison_type != "equal":
                    self._debug_tool.debug_log(f"Skipping key '{key}' due to type mismatch between threshold and value.", self.isDebug)
                    continue
                if isinstance(value, (dict, list, tuple)):
                    self._debug_tool.debug_log(f"Skipping key '{key}' because its value is of unsupported type ({type(value).__name__}).", self.isDebug)
                    continue
                if compare_ops[comparison_type](value): # Perform comparison
                    self._debug_tool.debug_log(f"Key '{key}' matches the condition: {value} {comparison_type} {threshold}.", self.isDebug)
                    matching_keys.append(key)

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
                cache = self._FileManager.load_json(f"{self._PARENT_DIR}/language/{lang}.json")
                if not cache.success:
                    raise FileNotFoundError(f"Language file for '{lang}' could not be loaded.")
                self._lang_cache[lang] = cache.data

            # Return text
            if key in self._lang_cache[lang]:
                return Result(True, None, None, self._lang_cache[lang][key])
            else:
                raise KeyError(f"Key '{key}' not found in language '{lang}'. Available keys: {list(self._lang_cache[lang].keys())}")
        except Exception as e:
            try:
                del self._lang_cache[lang]  # Clear cache on failure
            except KeyError:
                self._log.log_msg("warning", f"Attempted to clear non-existent cache for language '{lang}'.", self.No_Log)
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

class FileManager():
    """
    The FileManager class provides functionality to read and write various file formats.

    Currently supports only JSON file format, but other formats can be added in the future.

    1. JSON File Management: Provides functionality to safely read and write JSON files.
        - load_json: Loads JSON files as dictionaries.
        - save_json: Saves dictionaries as JSON files. (Atomic write applied)

    2. Atomic Write: Uses temporary files to safely save files and prevent data corruption during file saving.
    """
    def __init__(self, isTest: bool = False, isDebug: bool = False, logger = None, No_Log: bool = False):
        """
        initialize FileManager
        """
        print("Initializing FileManager...")
        # initialize directory
        self._PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._LOG_DIR = f"{Path(__file__).resolve().parent.parent}/logs"

        # initialize classes
        self._exception_tracker = ExceptionTracker()
        if logger is None:
            print("No logger provided, initializing default LoggerManager.")
            self._LOGGER_MANAGER = log.LoggerManager(base_dir=self._LOG_DIR, second_log_dir="FileManagerLogs")
            self._LOGGER_MANAGER.Make_logger("FileManager")
        self._logger = self._LOGGER_MANAGER.get_logger("FileManager") if logger is None else logger
        self._log = log.Log(logger=self._logger)
        self._debug_tool = DebugTool.DebugTool(logger=self._logger)

        # set variables
        self.isTest = isTest
        self.isDebug = isDebug
        self.No_Log = No_Log

        self._log.log_msg("info", "FileManager initialized successfully.", self.No_Log)

    def load_json(self, file_path: str) -> Result:
        """
        Function to load JSON files as dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._log.log_msg("info", f"JSON loaded successfully from {file_path}.", self.No_Log)
                return Result(True, None, None, json.load(f))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self._log.log_msg("error", f"Error loading JSON from {file_path}: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def load_file(self, file_path: str) -> Result:
        """
        Function to load files as strings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._log.log_msg("info", f"File loaded successfully from {file_path}.", self.No_Log)
                return Result(True, None, None, f.read())
        except Exception as e:
            self._log.log_msg("error", f"Error loading file from {file_path}: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def save_json(self, data: Optional[dict], file_path: str, key: str=None, serialization: bool=False) -> Result:
        """
        Function to save dictionaries as JSON files (Atomic write applied)
        - Only JSON files are supported. Other formats Use Atomic_write.
        - If 'key' is provided, the function updates the existing JSON file by adding or updating the specified key with the new data.
        - If 'key' is None, the function overwrites the entire JSON file with the new data.
        """
        try:
            # Prepare final data to save
            if key is not None:
                cache = self.load_json(file_path)
                if not cache.success:
                    raise ValueError(f"Failed to load existing JSON file: {file_path}")
                
                existing_data = cache.data
                existing_data[key] = data
                final_data = existing_data
            else:
                final_data = data
            
            # Perform atomic write
            self.Atomic_write(json.dumps(final_data, ensure_ascii=False, indent=4) if serialization else json.dumps(final_data), file_path)
            self._log.log_msg("info", f"JSON saved successfully to {file_path}.", self.No_Log)
            return Result(True, None, None, None)

        except Exception as e:
            self._log.log_msg("error", f"Error saving JSON to {file_path}: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
                
    def Atomic_write(self, data: Any, file_path: Union[str, Path]) -> Result:
        """
        Function to perform atomic write
        """
        temp_file_path = None  

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not data:
                raise ValueError("Data to write is empty or None.")

            # Atomic write: write to temporary file first
            with tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                encoding='utf-8', 
                dir=os.path.dirname(file_path), 
                prefix=os.path.basename(str(file_path)) + '.tmp.'
            ) as tmp:
                tmp.write(data)
                temp_file_path = tmp.name
            
            # Atomic move
            shutil.move(temp_file_path, file_path)
            self._log.log_msg("info", f"File written successfully to {file_path}.", self.No_Log)
            return Result(True, None, None, None)
            
        except Exception as e:
            # Clean up temporary file (on move failure)
            self._log.log_msg("error", f"Error during atomic write to {file_path}: {e}", self.No_Log)
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    self._log.log_msg("info", f"Temporary file deleted successfully: {temp_file_path}", self.No_Log)
                except (OSError, Exception) as e:
                    self._log.log_msg("error", f"Failed to delete temporary file {temp_file_path}: {e}", self.No_Log)
                    return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
            self._log.log_msg("error", f"Atomic write failed for {file_path}. Successfully cleaned up temporary files.", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def batch_process_json_threaded(self, files: List[str], batch_size: int=10) -> Result:
        """
        Function to process files in batches using multithreading.
        - files: List of file paths to process.
        - batch_size: Number of files to process in each batch.

        files example: ['path/to/file1.json', 'path/to/file2.json', ...]
        """
        try:
            def process_batch(batch_files: List[str]) -> List[dict]:
                results = []
                for file in batch_files:
                    result = self.load_json(file).data
                    results.append(result)
                return results
            
            if files is None or len(files) == 0:
                raise ValueError("files list is empty or None.")
            # Validate files list structure
            if not isinstance(files, list) or not all(isinstance(file, (str, Path)) for file in files): 
                raise ValueError("files must be a list of strings or Path objects.")
            # Adjust batch_size if necessary
            if batch_size <= 0:
                batch_size = 10
            if batch_size > len(files):
                batch_size = len(files)
            all_results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_batch, files[i:i+batch_size]) 
                           for i in range(0, len(files), batch_size)]
                for future in futures:
                    try:
                        all_results.extend(future.result())
                    except Exception as e:
                        self._log.log_msg("error", f"Error processing batch: {e}", self.No_Log)
            self._log.log_msg("info", "Batch processing of JSON files completed successfully.", self.No_Log)
            return Result(True, None, None, all_results)
        except Exception as e:
            self._log.log_msg("error", f"Error in batch_process_json_threaded: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def batch_process_write_json_threaded(self, data_list: List[Tuple[dict, str, bool]], batch_size: int=10) -> Result:
        """
        Function to write files in batches using multithreading.
        - data_list: List of tuples containing (data_dict, file_path, serialization).
        - batch_size: Number of files to write in each batch.
        - serialization: Whether to serialize JSON with indentation.

        data_list example: [(data1, 'path/to/file1.json', True), (data2, 'path/to/file2.json', False), ...]
        """
        try:
            def process_batch(batch_data: List[Tuple[dict, Union[str, Path], bool]]) -> Result:
                results = []
                for data, file_path, serialization in batch_data:
                    result = self.save_json(data, file_path, serialization=serialization)
                    results.append(result)
                return results
            
            if data_list is None or len(data_list) == 0:
                raise ValueError("data_list is empty or None.")
            # Validate data_list structure
            if not isinstance(data_list, list) or not all(isinstance(item, tuple) and len(item) == 3 and isinstance(item[0], dict) and isinstance(item[1], (str, Path)) and isinstance(item[2], bool) for item in data_list): 
                raise ValueError("data_list must be a list of tuples in the form (dict, str, bool).")
            # Adjust batch_size if necessary
            if batch_size <= 0:
                batch_size = 10
            if batch_size > len(data_list):
                batch_size = len(data_list)
            all_results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_batch, data_list[i:i+batch_size]) 
                           for i in range(0, len(data_list), batch_size)]
                for future in futures:
                    try:
                        all_results.extend(future.result())
                    except Exception as e:
                        self._log.log_msg("error", f"Error processing batch: {e}", self.No_Log)
            return Result(True, None, None, all_results)
        except Exception as e:
            self._log.log_msg("error", f"Error in batch_process_write_json_threaded: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

"""
example code with multi processing:

all_results = []
with mp.Pool(processes=4) as pool:
    futures = [pool.apply_async(process_batch, (data_list[i:i+batch_size],))
                for i in range(0, len(data_list), batch_size)]
    for future in futures:
        all_results.extend(future.get())
"""

a = AppCore()