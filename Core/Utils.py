# external modules

# internal modules
from Core import LogSys, AppCore, FileManager, Deco, Exception, DebugTool, ResultManager

class Utils:
    """
    Utility class for common helper functions
    """
    pass

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
        Result: Instance of Result for result representation
        ExtendedResult: Instance of ExtendedResult for extended result representation
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
        self.Result = None
        self.ExtendedResult = None

    def initialize(self, logger_manager = None, logger_name: str="Initializer"):
        """
        Method to initialize core components
        """
        self.LoggerManager = logger_manager or LogSys.LoggerManager()
        self.LoggerManager.Make_logger(logger_name)
        self.Log = LogSys.Log(logger=self.LoggerManager.get_logger(logger_name).data)
        self.AppCore = AppCore.AppCore(logger_manager=self.LoggerManager)
        self.GlobalVars = AppCore.GlobalVars()
        self.FileManager = FileManager(logger_manager=self.LoggerManager)
        self.Deco = Deco()
        self.ExceptionTracker = Exception.ExceptionTracker()
        self.DebugTool = DebugTool.DebugTool(logger=self.LoggerManager.get_logger(logger_name).data)
        self.ResultManager = ResultManager()
        self.Result = ResultManager.Result()
        self.ExtendedResult = ResultManager.ExtendedResult()