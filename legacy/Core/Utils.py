# external modules
from typing import Any, Tuple, Union, Optional, Dict

# internal modules
from Core import LogSys, AppCore, FileManager, Deco, Exception, DebugTool, ResultManager
from Core import Result

class Utils:
    """
    Utility class for common helper functions
    """
    
    def __init__(self):
        pass

    def get_app_version(self) -> Tuple[str, str]:
        """
        Method to get the application version

        - (version number, version stage)
        """
        return "0.0.1", "Alpha"
    
    def separation_line(self, length: int=50, char: str='-') -> str:
        """
        Method to generate a separation line string
        """
        return char * length
    
class Intializer:
    """
    Class for initializing core components

    Provides methods to initialize logging, app core, file manager, decorators, exception tracking, debug tools, and result management

    Attributes:
        LoggerManager: Instance of LoggerManager for logging
        Log: Instance of Log for logging messages
        AppCore: Instance of AppCore for application core functionalities
        GlobalVars: Instance of GlobalVars for global variables
        FileManager: Instance of FileManager for file operations
        Deco: Instance of Deco for decorators
        ExceptionTracker: Instance of ExceptionTracker for exception handling
        DebugTool: Instance of DebugTool for debugging utilities
        ResultManager: Instance of ResultManager for managing results ( ** Feature not implemented yet. Do not use anything other than Result and ExtendedResult. ** )
    """
    
    def __init__(self):
        self.LoggerManager = None
        self.Log = None
        self.AppCore = None
        self.GlobalVars = None
        self.FileManager = None
        self.Deco = None
        self.ExceptionTracker = None
        self.DebugTool = None
        self.ResultManager = None

    def initializer(self, logger_manager = None, logger_name: str="Initializer"):
        """
        Method to initializer core components
        """
        self.LoggerManager = logger_manager or LogSys.LoggerManager()
        self.LoggerManager.Make_logger(logger_name)
        self.Log = LogSys.Log(logger=self.LoggerManager.get_logger(logger_name).data)
        self.AppCore = AppCore.AppCore(logger_manager=self.LoggerManager)
        self.GlobalVars = GlobalVars()
        self.FileManager = FileManager(logger_manager=self.LoggerManager)
        self.Deco = Deco()
        self.ExceptionTracker = Exception.ExceptionTracker()
        self.DebugTool = DebugTool.DebugTool(logger=self.LoggerManager.get_logger(logger_name).data)
        self.ResultManager = ResultManager()

class GlobalVars:
    """
    The GlobalVars provide global variables.
    """
    def __init__(self):
        self.exception_tracker = Exception.ExceptionTracker()
        self.global_vars = {}
        
    def set(self, key: str, value: Any, overwrite: bool = True) -> Result:
        """
        Set global variable
        """
        try:
            vars_exist = self.exists(key)
            if not vars_exist.success:
                raise Exception(vars_exist.message)
            if vars_exist.data and not overwrite:
                raise ValueError(f"Global variable with key '{key}' already exists and overwrite is set to False.")
            self.global_vars[key] = value
            return Result(True, None, None, True)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def exists(self, key: str) -> Result:
        """
        Check if global variable exists
        """
        try:
            exists = key in self.global_vars
            return Result(True, None, None, exists)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def get(self, key: str) -> Result:
        """
        Get global variable
        """
        try:
            if not self.exists(key).data:
                raise KeyError(f"Global variable with key '{key}' does not exist.")
            return Result(True, None, None, self.global_vars[key])
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def delete(self, key: str) -> Result:
        """
        Delete global variable
        """
        try:
            if not self.exists(key).data:
                raise KeyError(f"Global variable with key '{key}' does not exist.")
            del self.global_vars[key]
            return Result(True, None, None, True)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def clear(self) -> Result:
        """
        Clear all global variables
        """
        try:
            self.global_vars.clear()
            return Result(True, None, None, True)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
class ClassNameUpper(type):
    """
    Metaclass to convert class names to uppercase
    """
    def __new__(cls, name, bases, attrs):
        name = name.upper()
        return super().__new__(cls, name, bases, attrs)