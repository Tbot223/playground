# external modules
import time

# internal modules

class Deco:
    """
    Decorator class

    Provides common decorators
    """
    def __init__(self):
        pass

    def count_run_time(self):
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
        