# external modules
import os
import json
import time
import shutil
from typing import Union, Optional, Tuple, List, Dict
import stat
from pathlib import Path

# internal modules
from Core import Result, AppCore, DebugTool, FileManager
from Core import LogSys as log
from Core.Exception import ExceptionTracker

# Global Variables

class StorageManager:
    """
    StorageManager handles save and load functionality.

    Performs data saving, loading, deletion, listing, validation, etc.
    All data is stored in JSON format.
    Default save path is ./{_PARENT_DIR}/saves/.
    Backup functionality is planned for future implementation.

    1. load_data(save_type, save_id="latest")
        - Loads specified type of data from a specific save ID.

    2. save_data(save_data, save_type, save_id)
        - Saves specified type of data to a specific save ID.

    3. save_all(data, metadata, save_id=None)
        - Saves all user, stocks data.
        - If save_id is None, generates a new ID.
        - If save_id is provided, overwrites data to that ID.
        - Use save_all when creating new saves.

    4. save_metadata(save_id)
        - Save metadata such as save time, user name, play time

    5. load_metadata(save_id)
        - Load saved metadata

    6. list_saves()
        - Returns all save IDs in the saves/ folder.
        
    7. delete_save(save_id)
        - Deletes the corresponding save folder.

    8. save_exists(save_id)
        - Checks if a specific save ID exists.

    9. validate_save(save_id)
        - Check existence of required files (user.json, stocks.json, etc.)
        - Return list of missing files

    10. get_latest_save_id()
        - Return the most recently created save ID

    11. backup_save(save_id)
        - Not needed currently, implement later if needed
    """
    def __init__(self, parent_dir: Union[str, Path] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))), isDebug: bool=False, isTest: bool=False, logger=None, No_Log: bool=False, 
                appcore: AppCore.AppCore = None, filemanager: FileManager = None, log_class: log.Log = None, logger_manager: log.LoggerManager = None, debug_tool: DebugTool.DebugTool = None):
        """
        Initialize StorageManager

        Dependency Injection available for: - It's not required to inject all these classes, only the ones you want to customize.
        - instance will create default instances if not provided.
            - AppCore : AppCore.AppCore
            - FileManager : FileManager
            - Log : log.Log
            - LoggerManager : log.LoggerManager
            - DebugTool : DebugTool.DebugTool
        """
        print("Initializing StorageManager...")
        # Initialize directories
        self._PARENT_DIR = parent_dir
        self._BASE_DIR = f"{self._PARENT_DIR}/saves"
        self._BACKUP_DIR = f"{self._PARENT_DIR}/backup"
        self._LOG_DIR = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/logs"
        os.makedirs(self._BASE_DIR, exist_ok=True)

        # Initialize classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = logger_manager or log.LoggerManager(base_dir=self._LOG_DIR, second_log_dir="StorageManagerLogs")
        self._logger_manager.Make_logger(name="StorageManager")
        self._logger = logger or self._logger_manager.get_logger("StorageManager").data
        self._log = log_class or log.Log(self._logger)
        self._file_manager = filemanager or FileManager(logger_manager=self._logger_manager)
        self._debug_tool = debug_tool or DebugTool.DebugTool(logger=self._logger)

        # Set Variables
        self.isDebug = isDebug
        self.isTest = isTest
        self.No_Log = No_Log

        self._log.log_msg("info", "StorageManager initialized successfully.", self.No_Log)

    def load_data(self, save_type: str, save_id: str="latest") -> Result:
        """
        Load data from /saves/(save_id)/(save_type).json.
        """
        try:
            if save_id == "latest":
                latest_save = self.get_latest_save_id()
                if not latest_save.success:
                    raise ValueError("Failed to get latest save ID.")
                save_id = latest_save.data
            file_path = f"{self._BASE_DIR}/{save_id}/{save_type}.json"
            load_result = self._file_manager.load_json(file_path)
            if not load_result.success:
                raise ValueError(f"Failed to load {save_type} data: {load_result.error}")
            self._log.log_msg("info", f"Successfully loaded {save_type} data.", self.No_Log)
            return Result(True, None, None, load_result.data)
        except Exception as e:
            self._log.log_msg("error", f"Error loading data: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def save_data(self, save_data: dict, save_type: str, save_id: str = None) -> Result:
        """
        Save data to /saves/(save_id)/(save_type).json.
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None. Use save_all() to create a new save.")
            file_path = f"{self._BASE_DIR}/{save_id}/{save_type}.json"
            self._file_manager.save_json(save_data, file_path)
            self._log.log_msg("info", f"Successfully saved {save_type} data.", self.No_Log)
            return Result(True, None, None, None)
        except Exception as e:
            self._log.log_msg("error", f"Error saving data: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def save_all(self, data: List[Dict]=None, metadata: dict=None, save_id: str=None) -> Result:
        """
        Save all input data such as user_data, world_data, etc.

        Args:
            data (list): List of data to save (required)
                - Each item must be in dict format.
                - Example: [{"user_data": user_data}, {"stocks_data": stocks_data}]
                - Using other formats is absolutely prohibited!
            metadata (dict): Metadata to save (optional)
                - Example: {"user_name": "tester", "playtime": 100}
        """
        try:
            if data is None:
                raise ValueError("Data must be provided as a list of dictionaries.")
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("All items in data must be of type dict.")
                if not isinstance(next(iter(item.values())), dict):
                    raise ValueError("All items in data must be of type dict.")
                if len(item) != 1:
                    raise ValueError("Each dictionary in data must contain exactly one key-value pair.")
            
            def save_item(item, save_id=None): # Internal function to save data
                if save_id is not None:
                    for key, value in item.items():
                        file_path = f"{self._BASE_DIR}/{save_id}/{key}.json"
                        self._file_manager.save_json(value, file_path)
                else: # Cannot create new save if save_id is None
                    raise ValueError("save_id cannot be None when saving individual items.(inner function, save_item)")

            if save_id is not None: # When save ID is provided
                if not os.path.exists(os.path.join(self._BASE_DIR, save_id)):
                    os.makedirs(os.path.join(self._BASE_DIR, save_id), exist_ok=True)
                self.save_metadata(save_id, metadata)
                for item in data:
                    save_item(item, save_id)
                return Result(True, None, None, None)
            else: # When save ID is not provided, generate new ID
                i = 1
                while True: # Create folders in order: save_1, save_2, ...
                    candidate = f"save_{i}" 
                    candidate_path = os.path.join(f"{self._BASE_DIR}/{candidate}") # saves/save_i
                    if not os.path.exists(candidate_path): # Create if folder doesn't exist
                        os.makedirs(candidate_path, exist_ok=True)
                        break
                    i += 1

                # Save new data
                self.save_metadata(candidate, metadata)
                for item in data:
                    save_item(item, candidate)
                self._log.log_msg("info", f"Successfully created new save: {candidate}", self.No_Log)
                return Result(True, None, None, None)
        except Exception as e:
            self._log.log_msg("error", f"Error saving all data: {e}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def load_save(self, save_id: str, required_files: List = None) -> Result:
        """
        Load all data from a specific save ID.
        """
        try:
            if save_id is None or save_id == "":
                raise ValueError("save_id cannot be None.")
            if required_files is None:
                raise ValueError("required_files must be provided as a list of filenames.")
            if not os.path.exists(os.path.join(self._BASE_DIR, save_id)):
                raise FileNotFoundError(f"Save ID '{save_id}' does not exist.")
            save_path = Path(self._BASE_DIR) / save_id
            files = os.listdir(save_path)
            data = {}
            for file in files:
                if not file.endswith(".json"):
                    self._log.log_msg("warning", f"Skipping non-JSON file: {file}", self.No_Log)
                    continue
                if file not in required_files:
                    self._log.log_msg("info", f"Skipping unrequired file: {file}", self.No_Log)
                    continue
                file_path = save_path / file
                load_result = self._file_manager.load_json(str(file_path))
                if not load_result.success or load_result.data is None:
                    raise ValueError(f"Failed to load {file}: {load_result.error}")
                data[file[:-5]] = load_result.data  # Remove .json extension
            self._log.log_msg("info", f"Successfully loaded save: {save_id}", self.No_Log)
            return Result(True, None, None, data)
        except Exception as e:
            self._log.log_msg("error", f"Error loading save {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def save_metadata(self, save_id: str, other_info: dict=None) -> Result:
        """
        Save metadata such as save time, user name, play time, etc.
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None.")

            metadata = {
                "timestamp": time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime()),
                }
            if other_info is not None:
                metadata.update(other_info)

            file_path = f"{self._BASE_DIR}/{save_id}/metadata.json"
            self._file_manager.save_json(metadata, file_path)
            self._log.log_msg("info", f"Successfully saved metadata for save ID: {save_id}", self.No_Log)
            return Result(True, None, None, None)
        except Exception as e:
            self._log.log_msg("error", f"Error saving metadata for save ID {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def load_metadata(self, save_id: str) -> Result:
        """
        Load saved metadata
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None.")
            if not os.path.exists(os.path.join(self._BASE_DIR, save_id)):
                raise FileNotFoundError(f"Save ID '{save_id}' does not exist.")
            file_path = f"{self._BASE_DIR}/{save_id}/metadata.json"
            metadata = self._file_manager.load_json(file_path)
            if not metadata.success:
                raise ValueError("Failed to load metadata.")
            if metadata.data is None:
                raise ValueError("Metadata is None.")
            self._log.log_msg("info", f"Successfully loaded metadata for save ID: {save_id}", self.No_Log)
            return Result(True, None, None, metadata.data)
        except Exception as e:
            self._log.log_msg("error", f"Error loading metadata for save ID {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def list_saves(self) -> Result:
        """
        Return all save IDs in the saves/ folder
        """
        try:
            saves = os.listdir(self._BASE_DIR)
            self._log.log_msg("info", f"Successfully listed saves. Total saves: {len(saves)}", self.No_Log)
            return Result(True, None, None, saves)
        except Exception as e:
            self._log.log_msg("error", f"Error listing saves: {str(e)}", self.No_Log)
            return Result(False, str(e), self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)
        
    def delete_save(self, save_id: str) -> Result:
        """
        Delete the corresponding save folder
        """
        try:
            save_path = os.path.join(self._BASE_DIR, save_id) # saves/save_id
            if os.path.exists(save_path):
                try:
                    shutil.rmtree(save_path) # Delete folder and all internal files
                except PermissionError:
                    self._log.log_msg("warning", f"PermissionError encountered while deleting {save_path}. Attempting to change file permissions and retry.", self.No_Log)
                    shutil.rmtree(save_path, onerror=lambda func, p, exc: (os.chmod(p, stat.S_IWRITE), func(p))) # Retry after changing permissions if deletion fails due to permission issues
                self._log.log_msg("info", f"Successfully deleted save ID: {save_id}", self.No_Log)
                return Result(True, None, None, None)
            else:
                raise FileNotFoundError(f"Save ID '{save_id}' is maybe already deleted or does not exist.")
        except Exception as e:
            self._log.log_msg("error", f"Error deleting save {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def save_exists(self, save_id: str) -> Result:
        """
        Check if a specific save ID exists
        """
        try:
            save_path = os.path.join(self._BASE_DIR, save_id)
            self._log.log_msg("info", f"Checked existence of save ID: {save_id}", self.No_Log)
            return Result(True, None, None, os.path.exists(save_path))
        except Exception as e:
            self._log.log_msg("error", f"Error checking existence of save {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def validate_save(self, save_id: str, required_files: List = None):
        """
        Check existence of required files (user.json, metadata.json, etc.)

        Args:
            required_files (list): List of required files (required)
            - Example: ["user.json", "stocks.json", "metadata.json"]
            - ValueError occurs if None
        """
        try:
            if required_files is None:
                raise ValueError("required_files must be provided as a list of filenames.")
            save_path = os.path.join(self._BASE_DIR, save_id)
            searched_file = os.listdir(save_path)
            missing_files = []
            for req_file in required_files:
                if req_file not in searched_file:
                    missing_files.append(req_file)
                else:
                    continue
            if missing_files != []:
                self._log.log_msg("warning", f"Missing files for save ID {save_id}: {missing_files}", self.No_Log)
                return Result(True, None, None, {"valid": False, "missing_files": missing_files})

            self._log.log_msg("info", f"All required files are present for save ID: {save_id}", self.No_Log)
            return Result(True, None, None, {"valid": True, "missing_files": None})
        except Exception as e:
            self._log.log_msg("error", f"Error validating save {save_id}: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

    def get_latest_save_id(self) -> Result:
        """
        Return the most recently created save ID
        """
        try:
            saves = self.list_saves()
            if not saves.success:
                raise ValueError("Failed to list saves.")
            latest_save = None
            latest_time = 0
            for save in saves.data:
                metadata = self.load_metadata(save)
                if isinstance(metadata, tuple) and metadata.success is False:
                    raise ValueError(f"Failed to load metadata for save: {save}")
                timestamp_str = metadata.data.get("timestamp", "")

                timestamp = time.mktime(time.strptime(timestamp_str, "%Y-%m-%d,%H:%M:%S"))
                if timestamp > latest_time:
                    latest_time = timestamp
                    latest_save = save
            if latest_save is None:
                raise ValueError("No valid saves found.")
            self._log.log_msg("info", f"Latest save ID is: {latest_save}", self.No_Log)
            return Result(True, None, None, latest_save)
        except Exception as e:
            self._log.log_msg("error", f"Error getting latest save ID: {str(e)}", self.No_Log)
            return Result(False, f"{type(e).__name__} :{str(e)}", self._exception_tracker.get_exception_location(e).data, self._exception_tracker.get_exception_info(e).data)

# Example usage:

"""
user_data = {"name": "Alice", "level": 5, "experience": 1500}
stocks_data = {"AAPL": 10, "GOOGL": 5, "TSLA": 2}
data = [    
        {"user_data": user_data}, 
        {"stocks_data": stocks_data}
       ]    
a = StorageManager().save_all(data)
print(a)
"""

# StorageManager().save_data({"name": "Alice", "level": 5, "experience": 150}, "user_data", "save_1")
    
# print(StorageManager().validate_save("save_1", ["user_data.json", "stocks_data.json", "metadata.json"]))

# print(StorageManager().get_latest_save_id())

# StorageManager().delete_save("save_1")

# print(StorageManager().list_saves())

# print(StorageManager().load_data("user_data"))

# print(StorageManager().load_metadata("save_2"))

# print(StorageManager().save_exists("save_2"))

"""
[StorageManager features that need to be updated]

    1. backup_save(save_id) - Not needed currently, implement later if needed
    - Create copies in backup/ folder when saving
    - Prepare for data corruption, can be linked with recovery functionality
    
"""