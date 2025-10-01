# external modules
import os
import json
import time
import shutil
from typing import Union, Optional, Tuple, List, Dict
import stat

# internal modules
from Core import Result, AppCore

class StorageManager:
    """
    StorageManager handles save and load functionality.

    Performs data saving, loading, deletion, listing, validation, etc.
    All data is stored in JSON format.
    Default save path is ./saves/.
    Backup functionality is planned for future implementation.

    1. load_data(save_type, save_id="latest")
        - Loads specified type of data from a specific save ID.

    2. save_data(save_data, save_type, save_id)
        - Saves specified type of data to a specific save ID.

    3. save_all(save_id=None)
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
    def __init__(self):
        self.core = AppCore.AppCore()
        self.FileManager = AppCore.FileManager()
        self.exception_tracker = AppCore.ExceptionTracker()
        self.base_dir = "saves"
        self.backup_dir = "backup"
        os.makedirs(self.base_dir, exist_ok=True)

    def load_data(self, save_type: str, save_id: str="latest") -> Result:
        """
        Load data from /saves/(save_id)/(save_type).json.
        """
        try:
            if save_id == "latest":
                latest_save = self.get_latest_save_id()
                if latest_save.success is False:
                    raise ValueError("Failed to get latest save ID.")
                save_id = latest_save.data
            file_path = f"saves/{save_id}/{save_type}.json"
            return Result(True, None, None, self.core.FileManager.load_json(file_path))
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_data(self, save_data: dict, save_type: str, save_id: str = None) -> Result:
        """
        Save data to /saves/(save_id)/(save_type).json.
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None. Use save_all() to create a new save.")
            file_path = f"saves/{save_id}/{save_type}.json"
            self.FileManager.save_json(save_data, file_path)
            return Result(True, None, None, None)

        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_all(self, data: List[Dict]=None, metadata: dict=None, save_id: str=None) -> Result:
        """
        Save all input data such as user_data, world_data, etc.

        Args:
            data (list): List of data to save (required)
                - Each item must be in dict format.
                - Example: [{"user_data": user_data}, {"stocks_data": stocks_data}]
                - Using other formats is absolutely prohibited!
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
                        file_path = f"saves/{save_id}/{key}.json"
                        self.FileManager.save_json(value, file_path)
                else: # Cannot create new save if save_id is None
                    raise ValueError("save_id cannot be None when saving individual items.(inner function, save_item)")

            if save_id is not None: # When save ID is provided
                if not os.path.exists(os.path.join(self.base_dir, save_id)):
                    os.makedirs(os.path.join(self.base_dir, save_id), exist_ok=True)
                self.save_metadata(save_id)
                for item in data: # Overwrite data to given ID
                    save_item(item, save_id)
                return Result(True, None, None, None)
            else: # When save ID is not provided, generate new ID
                i = 1
                while True: # Create folders in order: save_1, save_2, ...
                    candidate = f"save_{i}" 
                    candidate_path = os.path.join(self.base_dir, candidate) # saves/save_i
                    if not os.path.exists(candidate_path): # Create if folder doesn't exist
                        os.makedirs(candidate_path, exist_ok=True)
                        self.save_metadata(candidate)
                        for item in data:
                            save_item(item, candidate)
                        return Result(True, None, None, None)
                    i += 1
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

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

            file_path = f"saves/{save_id}/metadata.json"
            self.FileManager.save_json(metadata, file_path)
            return Result(True, None, None, None)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def load_metadata(self, save_id: str) -> Result:
        """
        Load saved metadata
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None.")
            if not os.path.exists(os.path.join(self.base_dir, save_id)):
                raise FileNotFoundError(f"Save ID '{save_id}' does not exist.")
            file_path = f"saves/{save_id}/metadata.json"
            metadata = self.FileManager.load_json(file_path)
            if not metadata.success:
                raise ValueError("Failed to load metadata.")
            if metadata.data is None:
                raise ValueError("Metadata is None.")
            return Result(True, None, None, metadata.data)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def list_saves(self) -> Result:
        """
        Return all save IDs in the saves/ folder
        """
        try:
            saves = os.listdir(self.base_dir)
            return Result(True, None, None, saves)
        except Exception as e:
            return Result(False, str(e), self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def delete_save(self, save_id: str) -> Result:
        """
        Delete the corresponding save folder
        """
        try:
            save_path = os.path.join(self.base_dir, save_id) # saves/save_id
            if os.path.exists(save_path):
                try:
                    shutil.rmtree(save_path) # Delete folder and all internal files
                except PermissionError:
                    shutil.rmtree(save_path, onerror=lambda func, p, exc: (os.chmod(p, stat.S_IWRITE), func(p))) # Retry after changing permissions if deletion fails due to permission issues
                return Result(True, None, None, None)
            else:
                raise FileNotFoundError(f"Save ID '{save_id}' is maybe already deleted or does not exist.")
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_exists(self, save_id: str) -> Result:
        """
        Check if a specific save ID exists
        """
        try:
            save_path = os.path.join(self.base_dir, save_id)
            return Result(True, None, None, os.path.exists(save_path))
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

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
            save_path = os.path.join(self.base_dir, save_id)
            searched_file = os.listdir(save_path)
            missing_files = []
            for req_file in required_files:
                if req_file not in searched_file:
                    missing_files.append(req_file)
                else:
                    continue
            if missing_files != []:

                return Result(True, None, None, {"valid": False, "missing_files": missing_files})

            return Result(True, None, None, {"valid": True, "missing_files": None})
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

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
            return Result(True, None, None, latest_save)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

# Test code

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