# external modules
import sys
import os
import platform
import time
import traceback
from typing import Any

# internal modules
from CoreV2.Result import Result

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
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_location, R23-54", traceback.format_exc())

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
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_info, R56-90", traceback.format_exc())
        
    def get_exception_return(self, error: Exception, user_input: Any=None, params: dict=None) -> dict:
        """
        Function to get exception information as a dictionary.
        This is a convenience function that wraps get_exception_info and extracts the data field from the Result object.
        """
        try:
            return Result(False, f"{type(error).__name__} :{str(error)}", self.get_exception_location(error).data, self.get_exception_info(error, user_input, params).data)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_return, R92-105", traceback.format_exc())