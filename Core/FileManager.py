# external modules
import os
import json
import tempfile
import shutil
from typing import Any, Union, List, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


# internal modules
from Core import log, Result, DebugTool
from Core.Exception import ExceptionTracker

class FileManager():
    """
    The FileManager class provides functionality to read and write various file formats.

    Currently supports only JSON file format, but other formats can be added in the future.

    1. JSON File Management: Provides functionality to safely read and write JSON files.
        - load_json: Loads JSON files as dictionaries.
        - save_json: Saves dictionaries as JSON files. (Atomic write applied)

    2. Atomic Write: Uses temporary files to safely save files and prevent data corruption during file saving.
    """
    def __init__(self, isTest: bool = False, isDebug: bool = False, second_log_dir: Union[str, Path] = None, logger = None, No_Log: bool = False, LOG_DIR: str = None,
                log_class: log.Log = None, logger_manager: log.LoggerManager = None, debug_tool: DebugTool.DebugTool = None):
        """
        initialize FileManager

        Dependency Injection available for: - It's not required to inject all these classes, only the ones you want to customize.
        - instance will create default instances if not provided.
            - Log : log.Log
            - LoggerManager : log.LoggerManager
            - DebugTool : DebugTool.DebugTool
        """
        print("Initializing FileManager...")
        # initialize directory
        self._PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._LOG_DIR = LOG_DIR or f"{Path(__file__).resolve().parent.parent}/logs"

        # initialize classes
        self._exception_tracker = ExceptionTracker()
        self._LOGGER_MANAGER = logger_manager or log.LoggerManager(base_dir=self._LOG_DIR, second_log_dir="FileManagerLogs")
        self._LOGGER_MANAGER.Make_logger("FileManager")
        self._logger = logger or self._LOGGER_MANAGER.get_logger("FileManager").data
        self._log = log_class or log.Log(logger=self._logger)
        self._debug_tool = debug_tool or DebugTool.DebugTool(logger=self._logger)

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
                data = json.load(f)
                self._log.log_msg("info", f"JSON loaded successfully from {file_path}.", self.No_Log)
                return Result(True, None, None, data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self._log.log_msg("error", f"Error loading JSON from {file_path}: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def load_file(self, file_path: Union[str, Path]) -> Result:
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
                cache = self.load_json(file_path)
                if not cache.success:
                    raise ValueError(f"Failed to load existing JSON file: {file_path}")
                
                existing_data = cache.data
                existing_data[key] = data
                final_data = existing_data
            else:
                final_data = data
            
            # Perform atomic write
            self.Atomic_write(json.dumps(final_data, ensure_ascii=False, indent=4) if serialization else json.dumps(final_data), file_path, True)
            self._log.log_msg("info", f"JSON saved successfully to {file_path}.", self.No_Log)
            return Result(True, None, None, None)

        except Exception as e:
            self._log.log_msg("error", f"Error saving JSON to {file_path}: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def Atomic_write(self, data: Any, file_path: Union[str, Path], No_log: bool = False) -> Result:
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
            self._log.log_msg("info", f"File written successfully to {file_path}.", No_log or self.No_Log)
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
        
    def load_json_threaded(self, file_paths: List[Union[str, Path]], workers: int = 2) -> Result:
        """
        Function to load multiple JSON files using multithreading.
        - file_paths: List of file paths to load.
        - workers: Number of threads to use.

        Returns a list of Result objects corresponding to each file load operation.
        """
        try:
            def process(file_path: Union[str, Path]) -> Result:
                return self.load_json(file_path).data
                
            if file_paths is None or len(file_paths) == 0:
                raise ValueError("file_paths list is empty or None.")
            if not isinstance(file_paths, list) or not all(isinstance(fp, (str, Path)) for fp in file_paths):
                raise ValueError("file_paths must be a list of strings or Path objects.")
            if not isinstance(workers, int) or workers <= 0:
                self._log.log_msg("warning", f"Invalid workers value: {workers}. Setting to default (2).", self.No_Log)
                workers = 2

            results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(process, file_path) for file_path in file_paths]
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        self._log.log_msg("error", f"Error processing file load: {e}", self.No_Log)
            self._log.log_msg("info", f"load_json_threaded completed successfully.", self.No_Log)
            return Result(True, None, None, results)
        except Exception as e:
            self._log.log_msg("error", f"Error in load_json_threaded: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def write_json_threaded(self, data_list: List[Tuple[dict, str, bool]], batch_size: int = 10, workers: int = 2) -> Result:
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
            if batch_size <= 0 or batch_size > len(data_list):
                self._log.log_msg("warning", f"Invalid batch_size value: {batch_size}. Setting to default (10 or len(data_list)).", self.No_Log)
                batch_size = 10 if batch_size <= 0 else len(data_list)
            if not isinstance(workers, int) or workers <= 0:
                self._log.log_msg("warning", f"Invalid workers value: {workers}. Setting to default (2).", self.No_Log)
                workers = 2
            all_results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(process_batch, data_list[i:i+batch_size]) 
                           for i in range(0, len(data_list), batch_size)]
                for future in as_completed(futures):
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