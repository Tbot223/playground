# external Modules
from pathlib import Path
from typing import Optional, Any
import time
import hashlib, secrets

# internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker
from CoreV2 import LogSys

class Utils:
    """
    Utility class providing various helper functions.

    Methods:
        - str_to_path(path_str: str) -> Result
            Convert a string to a Path object.
        
        - encrypt(data: str, algorithm: str='sha256') -> Result
            Encrypt a string using the specified algorithm.

        - pbkdf2_hmac(password: str, algorithm: str, iterations: int, salt_size: int) -> Result
            Generate a PBKDF2 HMAC hash of the given password.

        - verify_pbkdf2_hmac(password: str, salt_hex: str, hash_hex: str, iterations: int, algorithm: str) -> Result
            Verify a PBKDF2 HMAC hash of the given password.
    """
    
    def __init__(self, is_logging_enabled: bool=False,
                 base_dir: Optional[Path]=None,
                 logger_manager_instance: Optional[LogSys.LoggerManager]=None, logger: Optional[Any]=None, 
                 log_instance: Optional[LogSys.Log]=None):
        """
        Initialize Utils class.
        """
        # Initialize Paths
        self._BASE_DIR = base_dir or Path(__file__).resolve().parent.parent

        # Initialize Flags
        self.is_logging_enabled = is_logging_enabled

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.is_logging_enabled:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="utils")
            self._logger_manager.make_logger("UtilsLogger")
            self._logger = logger or self._logger_manager.get_logger("UtilsLogger").data
        self.log = log_instance or LogSys.Log(logger=self._logger)

        self.log.log_message("INFO", "Utils initialized.")

    # Internal Methods
    def _check_pbkdf2_params(self, password: str, algorithm: str, iterations: int, salt_size: int = 32) -> None:
        """
        Check parameters for PBKDF2 HMAC functions.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes (default: 32).

        Raises:
            ValueError: If any parameter is invalid.
        
        Example:
            >>> I'm Not recommending to call this method directly, It's for internal use.
            >>> utils = Utils()
            >>> utils._check_pdkdf2_params("my_password", "sha256", 100000, 32)
            >>> # No exception raised for valid parameters.
        """
        if not isinstance(password, str):
            raise ValueError("password must be a string")
        if algorithm not in ['sha1', 'sha256', 'sha512']:
            raise ValueError("Unsupported algorithm. Supported algorithms: 'sha1', 'sha256', 'sha512'")
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("iterations must be a positive integer")
        if not isinstance(salt_size, int) or salt_size <= 0:
            raise ValueError("salt_size must be a positive integer")

    # external Methods
    def str_to_path(self, path_str: str) -> Path:
        """
        Convert a string to a Path object.

        Args:
            - path_str : The string representation of the path.
            
        Returns:
            Result: A Result object containing the Path object.
        
        Example:
            >>> result = utils.str_to_path("/home/user/documents")
            >>> if result.success:
            >>>     path = result.data # Path object
            >>>     print(path.exists())
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(path_str, str):
                return Result(True, "already a Path object", None, path_str)

            return Result(True, None, None, Path(path_str))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def encrypt(self, data: str, algorithm: str='sha256') -> Result:
        """
        Encrypt a string using the specified algorithm.
        Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'

        Args:
            - data : The string to encrypt.
            - algorithm : The hashing algorithm to use. Defaults to 'sha256'

        Returns:
            Result: A Result object containing the encrypted string in hexadecimal format.

        Example:
            >>> result = utils.encrypt("my_secret_data", algorithm='sha256')
            >>> if result.success:
            >>>     encrypted_data = result.data
            >>>     print(encrypted_data)
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(data, str):
                raise ValueError("data must be a string")
            if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
                raise ValueError("Unsupported algorithm. Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'")

            hash_func = getattr(hashlib, algorithm)()
            hash_func.update(data.encode('utf-8'))
            encrypted_data = hash_func.hexdigest()

            self.log.log_message("INFO", f"Data encrypted using {algorithm}.")
            return Result(True, None, None, encrypted_data)
        except Exception as e:
            self.log.log_message("ERROR", f"Encryption failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def pbkdf2_hmac(self, password: str, algorithm: str, iterations: int, salt_size: int) -> Result:
        """
        Generate a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns a dict containing the salt (hex), hash (hex), iterations, and algorithm used.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes.

        Returns:
            Result: A Result object containing a dict with the following keys:
        
        Example:
            >>> result = utils.pbkdf2_hmac("my_password", "sha256", 100000, 32)
            >>> if result.success:
            >>>     hash_info = result.data
            >>>     print(hash_info)
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations, salt_size)
            
            salt = secrets.token_bytes(salt_size)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

            salt_hex = salt.hex()
            hash_hex = hash_bytes.hex()
            result = {
                "salt_hex": salt_hex,
                "hash_hex": hash_hex,
                "iterations": iterations,
                "algorithm": algorithm
            }

            self.log.log_message("INFO", f"PBKDF2 HMAC hash generated using {algorithm} with {iterations} iterations.")
            return Result(True, None, None, result)
        except Exception as e:
            self.log.log_message("ERROR", f"PBKDF2 HMAC hash generation failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def verify_pbkdf2_hmac(self, password: str, salt_hex: str, hash_hex: str, iterations: int, algorithm: str) -> Result:
        """
        Verify a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns True if the password matches the hash, False otherwise.

        Args:
            - password : The password string to verify.
            - salt_hex : The salt in hexadecimal format.
            - hash_hex : The hash in hexadecimal format.
            - iterations : Number of iterations.
            - algorithm : The hashing algorithm to use.

        Returns:
            Result: A Result object containing a boolean indicating whether the password matches the hash.

        Example:
            >>> hash_info = {
            >>>     "salt_hex": "a1b2c3d4e5f6...",
            >>>     "hash_hex": "abcdef123456...",
            >>>     "iterations": 100000,
            >>>     "algorithm": "sha256"
            >>> }
            >>> result = utils.verify_pbkdf2_hmac("my_password", hash_info["salt_hex"], hash_info["hash_hex"], hash_info["iterations"], hash_info["algorithm"])
            >>> if result.success:
            >>>     is_valid = result.data
            >>>     print(is_valid)  # True or False
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations)
            if not isinstance(salt_hex, str) or not isinstance(hash_hex, str):
                raise ValueError("salt_hex and hash_hex must be strings")
            
            salt = bytes.fromhex(salt_hex)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)
            computed_hash_hex = hash_bytes.hex()

            is_valid = computed_hash_hex == hash_hex
            self.log.log_message("INFO", f"PBKDF2 HMAC hash verification using {algorithm} with {iterations} iterations. Result: {is_valid}")
            return Result(True, None, None, is_valid)
        except Exception as e:
            self.log.log_message("ERROR", f"PBKDF2 HMAC hash verification failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
class DecoratorUtils:
    """
    This class provides utility decorators for various purposes.

    Methods:
        - count_runtime() -> function
            Decorator to measure and print the execution time of a function.
    """

    
    def __init__(self):
        self._exception_tracker = ExceptionTracker()

    # Internal Methods

    # external Methods
    @staticmethod
    def count_runtime():
        """
        Decorator to measure and print the execution time of a function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                run_time = end_time - start_time
                print(f"This ran for {run_time:.4f} seconds.")
                return result
            return wrapper
        return decorator
    
class GlobalVars:
    """
    This class manages global variables in a controlled manner.

    Recommended usage:
    - Beginners use explicit methods.
    - Advanced users can use attribute access or call syntax.

    Methods:
        - set(key: str, value: object, overwrite) -> Result
            Set a global variable.
        
        - get(key: str) -> Result
            Get a global variable.

        - delete(key: str) -> Result
            Delete a global variable.

        - clear() -> Result
            Clear all global variables.

        - list_vars() -> Result
            List all global variables.

        - exists(key: str) -> Result
            Check if a global variable exists.

        # internal Methods
        - __getattr__(name) 
            Get a global variable by attribute access.

        - __setattr__(name, value)
            Set a global variable by attribute access.  

        - __call__(key: str, value: Optional[object], overwrite: bool) -> Result 
            Get or set a global variable using call syntax.

    Example:
        >>> globals = GlobalVars()
        >>> globals.set("api_key", "12345", overwrite=True)
        >>> result = globals.get("api_key")
        >>> if result.success:
        >>>     print(result.data)  # Output: 12345
        >>> else:
        >>>     print(result.error)

        >>> # or using attribute access:

        >>> globals.api_key = "12345"
        >>> print(globals.api_key)  # Output: 12345
        
        >>> # or using call syntax:

        >>> globals("api_key", "12345", overwrite=True)
        >>> print(globals("api_key").data)  # Output: 12345
    """
    
    def __init__(self, is_logging_enabled: bool=False,
                 base_dir: Optional[Path]=None,
                 logger_manager_instance: Optional[LogSys.LoggerManager]=None, logger: Optional[Any]=None, 
                 log_instance: Optional[LogSys.Log]=None):
        
        # Set initialization flag to bypass __setattr__ during __init__
        object.__setattr__(self, '_initializing', True)
        object.__setattr__(self, 'vars', {})
        
        # Initialize Paths
        self._BASE_DIR = base_dir or Path(__file__).resolve().parent.parent

        # Initialize Flags
        self.is_logging_enabled = is_logging_enabled

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.is_logging_enabled:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="global_vars")
            self._logger_manager.make_logger("GlobalVarsLogger")
            self._logger = logger or self._logger_manager.get_logger("GlobalVarsLogger").data
        self.log = log_instance or LogSys.Log(logger=self._logger)
        
        # Initialization complete
        object.__setattr__(self, '_initializing', False)
        
    def set(self, key: str, value: object, overwrite: bool=False) -> Result:
        """
        Set a global variable.
        
        Args:
            - key : The name of the global variable.
            - value : The value to set.
            - overwrite : If True, overwrite existing variable. Defaults to False.

        Returns:
            Result: A Result object indicating success or failure.
        
        Example:
            >>> globals = GlobalVars()
            >>> result = globals.set("api_key", "12345", overwrite=True)
            >>> if result.success:
            >>>     print(result.data)  # Output: Global variable 'api_key' set.
            >>> else:
            >>>     print(result.error)
        """
        try:
            if self.exists(key).data and not overwrite:
                raise KeyError(f"Global variable '{key}' already exists.")
            if key is None or not isinstance(key, str) or key.strip() == "":
                raise ValueError("key must be a non-empty string.")
            
            self.vars[key] = value
            self.log.log_message("INFO", f"Global variable '{key}' set.")
            return Result(True, None, None, f"Global variable '{key}' set.")
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to set global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def get(self, key: str) -> Result:
        """
        Get a global variable.

        Args:
            - key : The name of the global variable.

        Returns:
            Result: A Result object containing the value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.get("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not self.exists(key):
                raise KeyError(f"Global variable '{key}' does not exist.")
            
            self.log.log_message("INFO", f"Global variable '{key}' accessed.")
            return Result(True, None, None, self.vars[key])
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to get global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def delete(self, key: str) -> Result:
        """
        Delete a global variable.

        Args:
            - key : The name of the global variable.
        
        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.delete("api_key")
            >>> if result.success and not globals.exists("api_key").data:
            >>>     print("api_key deleted successfully.")
            >>> else:
            >>>     print("Failed to delete api_key.")
        """
        try:
            if not self.exists(key):
                raise KeyError(f"Global variable '{key}' does not exist.")
            
            del self.vars[key]
            self.log.log_message("INFO", f"Global variable '{key}' deleted.")
            return Result(True, None, None, f"Global variable '{key}' deleted.")
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to delete global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def clear(self) -> Result:
        """
        Clear all global variables.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.clear()
            >>> if result.success and len(globals.list_vars().data) == 0:
            >>>     print("All global variables cleared.")
            >>> else:
            >>>     print(result.error)
        """
        try:
            for name in list(self.vars.keys()):
                del self.vars[name]

            self.log.log_message("INFO", "All global variables cleared.")
            return Result(True, None, None, "All global variables cleared.")
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to clear global variables: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def list_vars(self) -> Result:
        """
        List all global variables.

        Returns:
            Result: A Result object containing a list of global variable names.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.list_vars()
            >>> if result.success:
            >>>     print(result.data)  # Output: ['api_key', 'user_id']
            >>> else:
            >>>     print(result.error)
        """
        try:

            self.log.log_message("INFO", "Listing all global variables.")
            return Result(True, None, None, list(self.vars.keys()))
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to list global variables: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def exists(self, key: str) -> Result:
        """
        Check if a global variable exists.

        Args:
            - key : The name of the global variable.

        Returns:
            Result: A Result object containing a boolean indicating existence.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.exists("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: True
            >>> else:
            >>>     print(result.error)
        """
        try:
            exists = key in self.vars
            self.log.log_message("INFO", f"Checked existence of global variable '{key}': {exists}")
            return Result(True, None, None, exists)
        except Exception as e:
            self.log.log_message("ERROR", f"Failed to check existence of global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def __getattr__(self, name):
        """
        Get a global variable by attribute access.

        Args:
            - name : The name of the global variable.

        Returns:
            The value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345"
            >>> print(globals.api_key)  # Output: 12345 ( this part uses __getattr__ )
        """
        try:
            if not self.exists(name).data:
                raise KeyError(f"Global variable '{name}' does not exist.")
            return self.vars[name]
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __setattr__(self, name, value):
        """
        Set a global variable by attribute access.

        Args:
            - name : The name of the global variable.
            - value : The value to set.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345" ( this part uses __setattr__ )
            >>> print(globals.api_key)  # Output: 12345
        """
        # During initialization, use normal attribute setting
        try:
            if object.__getattribute__(self, '_initializing'):
                object.__setattr__(self, name, value)
                return
        except AttributeError:
            # _initializing not set yet, must be during early init
            object.__setattr__(self, name, value)
            return
        
        # After initialization, store in vars dict
        try:
            if name is None or not isinstance(name, str) or name.strip() == "":
                raise ValueError("name must be a non-empty string.")
            
            vars_dict = object.__getattribute__(self, 'vars')
            vars_dict[name] = value
        except Exception as e:
            exception_tracker = object.__getattribute__(self, '_exception_tracker')
            return exception_tracker.get_exception_return(e)
        
    def __call__(self, key: str, value: Optional[object]=None, overwrite: bool=False) -> Result:
        """
        Get or set a global variable using call syntax.
        If value is provided, set the variable; otherwise, get it.

        Args:
            - key : The name of the global variable.
            - value : The value to set (optional).
            - overwrite : If True, overwrite existing variable when setting. Defaults to False.

        Returns:
            Result: A Result object containing the value when getting, or indicating success/failure when setting

        Example:
            >>> globals = GlobalVars()
            >>> globals("api_key", "12345", overwrite=True)  # Set api_key
            >>> result = globals("api_key")  # Get api_key
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            if value is not None:
                return self.set(key, value, overwrite)
            else:
                return self.get(key)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)