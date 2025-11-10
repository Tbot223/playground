# external Modules
from pathlib import Path

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

    # Internal Methods

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

class NameDecorator:
    """
    Placeholder class for NameDecorator in CoreV2.
    Currently, no functionality is implemented here.
    """
    
    def __init__(self):
        self ._exception_tracker = ExceptionTracker()

        self.names = {}

    # Internal Methods
    def _to_pascal(self, name: str) -> str:
        """
        Convert name to PascalCase.
        """
        parts = name.replace('_', ' ').replace('-', ' ').split()
        pascal_name = ''.join(word.capitalize() for word in parts)
        return pascal_name

    # external Methods
    def register(self, name: str, obj: object) -> Result:
        """
        Register an object with a name.
        """
        try:
            if not isinstance(name, str):
                raise ValueError("name must be a string")
            if hasattr(self, name):
                raise ValueError(f"An object with name '{name}' is already registered.")
            
            pascal_name = self._to_pascal(name)
            self.names[pascal_name] = name
            super().__setattr__(name, obj)
            return Result(True, None, None, f"Object registered with name '{name}'")
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
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        for name in list(self.__dict__.keys()):
            if not name.startswith('_'):
                super().__delattr__(name)
        self .names.clear()
        return False