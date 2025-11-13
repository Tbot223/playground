# external Modules
from pathlib import Path
from typing import Any, Tuple, Optional
import time
import hashlib, secrets

# internal Modules
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTracker

class Utils:
    """
    Placeholder class for Utils in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self):
        self ._exception_tracker = ExceptionTracker()

        self.DEFULT_ITERATIONS = 300000
        self.DEFAULT_SALT_SIZE = 32

    # Internal Methods
    def _check_pdkdf2_params(self, password: str, algorithm: str, iterations: int, salt_size: int = 32) -> None:
        """
        Check parameters for PBKDF2 HMAC functions.
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
        """
        try:
            if not isinstance(path_str, str):
                raise ValueError("path_str must be a string")

            return Result(True, None, None, Path(path_str))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def encrypt(self, data: str, algorithm: str='sha256') -> Result:
        """
        Encrypt a string using the specified algorithm.
        Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'
        """
        try:
            if not isinstance(data, str):
                raise ValueError("data must be a string")
            if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
                raise ValueError("Unsupported algorithm. Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'")

            hash_func = getattr(hashlib, algorithm)()
            hash_func.update(data.encode('utf-8'))
            encrypted_data = hash_func.hexdigest()
            return Result(True, None, None, encrypted_data)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def pbkdf2_hmac(self, password: str, algorithm: str, iterations: int, salt_size: int) -> Result:
        """
        Generate a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns a dict containing the salt (hex), hash (hex), iterations, and algorithm used.
        """
        try:
            self._check_pdkdf2_params(password, algorithm, iterations, salt_size)
            
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

            return Result(True, None, None, result)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def verify_pbkdf2_hmac(self, password: str, salt_hex: str, hash_hex: str, iterations: int, algorithm: str) -> Result:
        """
        Verify a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns True if the password matches the hash, False otherwise.
        """
        try:
            self._check_pdkdf2_params(password, algorithm, iterations)
            if not isinstance(salt_hex, str) or not isinstance(hash_hex, str):
                raise ValueError("salt_hex and hash_hex must be strings")
            
            salt = bytes.fromhex(salt_hex)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)
            computed_hash_hex = hash_bytes.hex()

            is_valid = computed_hash_hex == hash_hex
            return Result(True, None, None, is_valid)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
class DecoratorUtils:
    """
    Placeholder class for DecoratorUtils in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self):
        self ._exception_tracker = ExceptionTracker()

    # Internal Methods

    # external Methods
    def conut_runtime(self):
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

class NameDecorator:
    """
    Placeholder class for NameDecorator in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self):
        self ._exception_tracker = ExceptionTracker()

        self.names = {}

    # Internal Methods
    @staticmethod
    def _to_pascal(name: str) -> str:
        """
        Convert name to PascalCase.
        """
        parts = name.replace('_', ' ').replace('-', ' ').split()
        pascal_name = ''.join(word.capitalize() for word in parts)
        return pascal_name

    # external Methods
    def register(self, name: str, obj: object, manual_name: bool=False) -> Result:
        """
        Register an object with a name.
        """
        try:
            if not isinstance(name, str):
                raise ValueError("name must be a string")
            changed_name = self._to_pascal(name) if not manual_name else name
            if hasattr(self, changed_name):
                raise ValueError(f"An object is already registered with the name '{changed_name}'")
            if hasattr(self, name):
                raise ValueError(f"An object is already registered with the name '{name}'")
            
            self.names[changed_name] = f"{obj=}".split('=')[0]
            super().__setattr__(changed_name, obj)
            return Result(True, None, None, f"Object registered with name '{changed_name}' ( original name: '{name}' )")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
    def unregister(self, name: str) -> Result:
        """
        Unregister an object by name. ( name is must be pascal case )
        """
        try:
            if not hasattr(self, name):
                raise ValueError(f"No object registered with name '{name}'")
            
            self.names.pop(name, None)
            super().__delattr__(name)
            return Result(True, None, None, f"Object unregistered with name '{name}'")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def list_objects(self) -> Result:
        """
        List all registered object names.
        """
        try:
            return Result(True, None, None, self.names)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __setattr__(self, name, value):
        """
        Set an object by name.
        """
        try:
            super().__setattr__(name, value)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __getattr__(self, name):
        """
        Get an object by name.
        """
        try:
            if not hasattr(self, name):
                raise AttributeError(f"No object registered with name '{name}'")
            return super().__getattribute__(name)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
class GlobalVars:
    """
    Placeholder class for GlobalVars in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self):
        self ._exception_tracker = ExceptionTracker()
        
    def set(self, key: str, value: object, overwrite: bool=False) -> Result:
        try:
            if hasattr(self, key) and not overwrite:
                raise KeyError(f"Global variable '{key}' already exists.")
            
            super().__setattr__(key, value)
            return Result(True, None, None, f"Global variable '{key}' set.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def get(self, key: str) -> Result:
        """
        Get a global variable.
        """
        try:
            if not self.exists(key):
                raise KeyError(f"Global variable '{key}' does not exist.")
            return Result(True, None, None, super().__getattribute__(key))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def delete(self, key: str) -> Result:
        """
        Delete a global variable.
        """
        try:
            if not self.exists(key):
                raise KeyError(f"Global variable '{key}' does not exist.")
            
            super().__delattr__(key)
            return Result(True, None, None, f"Global variable '{key}' deleted.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def clear(self) -> Result:
        """
        Clear all global variables.
        """
        try:
            for name in list(vars(self).keys()):
                if name.startswith('_'):
                    continue
                super().__delattr__(name)
            return Result(True, None, None, "All global variables cleared.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def list_vars(self) -> Result:
        """
        List all global variables.
        """
        try:
            return Result(True, None, None, list(vars(self).keys()))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def exists(self, key: str) -> Result:
        """
        Check if a global variable exists.
        """
        try:
            exists = hasattr(self, key)
            return Result(True, None, None, exists)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __getattr__(self, name):
        """
        Get a global variable by attribute access.
        """
        try:
            self.exists(name)
            return super().__getattribute__(name)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __setattr__(self, name, value):
        """
        Set a global variable by attribute access.
        """
        try:
            super().__setattr__(name, value)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __call__(self, key: str, value: Optional[object]=None, overwrite: bool=False) -> Result:
        """
        Get or set a global variable using call syntax.
        If value is provided, set the variable; otherwise, get it.
        """
        try:
            if value is not None:
                return self.set(key, value, overwrite)
            else:
                return self.get(key)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)