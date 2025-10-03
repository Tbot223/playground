# external modules
import json
import os
import tempfile
import shutil
import subprocess
import traceback
import time
from typing import NamedTuple
from typing import Any, Dict, List, Tuple, Union, Optional
import platform
import sys
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

# internal modules
from Core import Result

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
    SCREEN_CLEAR_LINES = 50  # Magic number as constant

    def __init__(self):
        self.parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.makedirs(f"{self.parent_dir}/language", exist_ok=True)
        self.lang = [os.path.splitext(file)[0] for file in os.listdir(f"{self.parent_dir}/language")]
        self._lang_cache = {}  # 언어 캐시 딕셔너리
        self.FileManager = FileManager()
        self.exception_tracker = ExceptionTracker()

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
                raise ValueError("json_data must be a dictionary.")
            if isinstance(threshold, (dict, list, tuple)): # Check threshold type
                raise ValueError("Threshold of type dict, list, or tuple is not supported.")
            if comparison_type not in ["above", "below", "equal"]: # Check comparison type
                raise ValueError("comparison_type must be 'above', 'below', or 'equal'.")

            compare_ops = {
                "above": lambda v: v > threshold, # '>' operator
                "below": lambda v: v < threshold, # '<' operator
                "equal": lambda v: v == threshold # '==' operator
            }

            for key, value in json_data.items(): # Iterate through dictionary
                if isinstance(threshold, str) and not isinstance(value, str):
                    continue
                if not isinstance(threshold, str) and isinstance(value, str):
                    continue
                if isinstance(value, (dict, list, tuple)): # If value is dict, list, tuple
                    continue
                if compare_ops[comparison_type](value): # Perform comparison
                    matching_keys.append(key)

            return Result(True, None, None, matching_keys)
            
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def getTextByLang(self, lang: str, key: str) -> Result:
        """
        Function to return text according to language settings

        No fallback mechanism.
        Must verify that language and key are valid before calling.
        Cache initialization and exception handling on failure.
        """
        try:
            if lang not in self.lang: # Check language
                raise ValueError(f"Language '{lang}' not supported. Available languages: {self.lang}")

            # Check cache
            if lang not in self._lang_cache:
                cache = self.FileManager.load_json(f"{self.parent_dir}/language/{lang}.json")
                if not cache.success:
                    raise FileNotFoundError(f"Language file for '{lang}' could not be loaded.")
                self._lang_cache[lang] = cache.data

            # Return text
            if key in self._lang_cache[lang]:
                return Result(True, None, None, self._lang_cache[lang][key])
            else:
                raise KeyError(f"Key '{key}' not found in language '{lang}'. Available keys: {list(self._lang_cache[lang].keys())}")
        except Exception as e:
            self._lang_cache = {}  # Initialize cache
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)


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
    def __init__(self):
        self.exception_tracker = ExceptionTracker()

    def load_json(self, file_path: str) -> Result:
        """
        Function to load JSON files as dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return Result(True, None, None, json.load(f))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def load_file(self, file_path: str) -> Result:
        """
        Function to load files as strings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return Result(True, None, None, f.read())
        except Exception as e:
            print(f"Error loading file from {file_path}: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_json(self, data: dict, file_path: str, key: str=None, serialization: bool=False) -> Result:
        """
        Function to save dictionaries as JSON files (Atomic write applied)
        - Only JSON files are supported. Other formats Use Atomic_write.
        - If 'key' is provided, the function updates the existing JSON file by adding or updating the specified key with the new data.
        - If 'key' is None, the function overwrites the entire JSON file with the new data.
        """
        try:
            # Prepare final data to save
            if key is not None:
                if os.path.exists(file_path):
                    cache = self.load_json(file_path)
                else:
                    raise FileNotFoundError(f"File '{file_path}' does not exist for updating with key '{key}'.")
                if not cache.success:
                    raise ValueError(f"Failed to load existing JSON file: {file_path}")
                
                existing_data = cache.data
                existing_data[key] = data
                final_data = existing_data
            else:
                final_data = data
            
            # Perform atomic write
            self.Atomic_write(json.dumps(final_data, ensure_ascii=False, indent=4) if serialization else json.dumps(final_data), file_path)
            return Result(True, None, None, None)

        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
                
    def Atomic_write(self, data: str, file_path: str) -> Result:
        """
        Function to perform atomic write
        """
        temp_file_path = None  

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Atomic write: write to temporary file first
            with tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                encoding='utf-8', 
                dir=os.path.dirname(file_path), 
                prefix=os.path.basename(file_path) + '.tmp.'
            ) as tmp:
                tmp.write(data)
                temp_file_path = tmp.name
            
            # Atomic move
            shutil.move(temp_file_path, file_path)
            return Result(True, None, None, None)
            
        except Exception as e:
            # Clean up temporary file (on move failure)
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (OSError, Exception) as e:
                    return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def batch_process_json(self, files: List[str], batch_size: int=10) -> Result:
        """
        Function to process files in batches using multithreading.
        - files: List of file paths to process.
        - batch_size: Number of files to process in each batch.

        files example: ['path/to/file1.json', 'path/to/file2.json', ...]
        """
        try:
            def process_batch(batch_files: List[str]) -> List[Result]:
                results = []
                for file in batch_files:
                    result = self.load_json(file).data
                    results.append(result)
                return results

            all_results = []
            with mp.Pool(processes=4) as pool:
                futures = [pool.apply_async(process_batch, (files[i:i+batch_size],))
                           for i in range(0, len(files), batch_size)]
                for future in futures:
                    all_results.extend(future.get())
            return Result(True, None, None, all_results)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def batch_process_json_threaded(self, files: List[str], batch_size: int=10) -> Result:
        """
        Function to process files in batches using multithreading.
        - files: List of file paths to process.
        - batch_size: Number of files to process in each batch.

        files example: ['path/to/file1.json', 'path/to/file2.json', ...]
        """
        try:
            def process_batch(batch_files: List[str]) -> List[Result]:
                results = []
                for file in batch_files:
                    result = self.load_json(file).data
                    results.append(result)
                return results
            
            all_results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_batch, files[i:i+batch_size]) 
                           for i in range(0, len(files), batch_size)]
                for future in futures:
                    all_results.extend(future.result())
            return Result(True, None, None, all_results)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def batch_process_write_json(self, data_list: List[Tuple[dict, str]], batch_size: int=10, serialization: bool=False) -> Result:
        """
        Function to write files in batches using multithreading.
        - data_list: List of tuples containing (data_dict, file_path).
        - batch_size: Number of files to write in each batch.
        - serialization: Whether to serialize JSON with indentation.

        data_list example: [(data1, 'path/to/file1.json'), (data2, 'path/to/file2.json'), ...]
        """
        try:
            def process_batch(batch_data: List[Tuple[dict, str]]) -> List[Result]:
                results = []
                for data, file_path in batch_data:
                    result = self.save_json(data, file_path, serialization=serialization)
                    results.append(result)
                return results

            all_results = []
            with mp.Pool(processes=4) as pool:
                futures = [pool.apply_async(process_batch, (data_list[i:i+batch_size],))
                           for i in range(0, len(data_list), batch_size)]
                for future in futures:
                    all_results.extend(future.get())
            return Result(True, None, None, all_results)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def batch_process_write_json_threaded(self, data_list: List[Tuple[dict, str]], batch_size: int=10, serialization: bool=False) -> Result:
        """
        Function to write files in batches using multithreading.
        - data_list: List of tuples containing (data_dict, file_path).
        - batch_size: Number of files to write in each batch.
        - serialization: Whether to serialize JSON with indentation.
        
        data_list example: [(data1, 'path/to/file1.json'), (data2, 'path/to/file2.json'), ...]
        """
        try:
            def process_batch(batch_data: List[Tuple[dict, str]]) -> List[Result]:
                results = []
                for data, file_path in batch_data:
                    result = self.save_json(data, file_path, serialization=serialization)
                    results.append(result)
                return results
            
            all_results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_batch, data_list[i:i+batch_size]) 
                           for i in range(0, len(data_list), batch_size)]
                for future in futures:
                    all_results.extend(future.result())
            return Result(True, None, None, all_results)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
                
class ExceptionTracker():
    """
    The ExceptionTracker class provides functionality to track location information when exceptions occur and return related information.
    
    1. Exception Location Tracking: Provides functionality to track where exceptions occur and return related information.
        - get_exception_location: Returns the location where the exception occurred.

    2. Exception Information Tracking: Provides functionality to track exception information and return related information.
        - get_exception_info: Returns information about the exception.
    """

    def __init__(self):
        # Cache system information
        # Safely get current working directory
        try:
            cwd = os.getcwd()
        except Exception:
            cwd = "<Permission Denied or Unavailable>"

        self._system_info = {
            "OS": platform.system(),
            "OS_version": platform.version(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Python_Version": platform.python_version(),
            "Python_Executable": sys.executable,
            "Current_Working_Directory": cwd
        }

    def get_exception_location(self, error: Exception) -> Result:
        """
        Function to track where exceptions occurred and return related information
        - Return information is included as a string in the data of the Result object.
        - Format (str): '{file}', line {line}, in {function}'
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame
            return Result(True, None, None, f"'{frame.filename}', line {frame.lineno}, in {frame.name}")
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            return Result(False, f"{type(e).__name__} :{str(e)}", "AppCore.ExceptionTracker.get_exception_location, R341-383", traceback.format_exc())

    def get_exception_info(self, error: Exception, user_input: Any=None, params: dict=None) -> Result:
        """
        Function to track exception information and return related information
        
        The error data dict includes traceback, location information, occurrence time, input context, etc.
        
        - error_info (dict):
            See Readme.md
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame
            error_info = {
                "success": False,
                "error":{
                    "type": type(error).__name__ if error else "UnknownError", 
                    "message": str(error) if error else "No exception information available"
                },
                "location": {
                    "file": frame.filename if frame else "Unknown",
                    "line": frame.lineno if frame else -1,
                    "function": frame.name if frame else "Unknown"
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "input_context": {
                    "user_input": user_input,
                    "params": params
                },
                "traceback": traceback.format_exc(),
                "computer_info": self._system_info
            }
            return Result(True, None, None, error_info)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            return Result(False, f"{type(e).__name__} :{str(e)}", "AppCore.ExceptionTracker.get_exception_location, R385-419", traceback.format_exc())