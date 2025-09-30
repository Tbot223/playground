# playground
This repository is my small lab — a place where I experiment with system design, exception handling, and structural ideas.

AppCore.py and StorageManager.py will have more detailed development process in other repositories!
(stock-game)

## Result

'''python
Result
    (
    success: bool,
    error: Optional[str],
    context: Optional[str],
    data: Any
    )

error_info(Result.data)

    {
        "success": bool,
        "error": {
            "type": "ExceptionType",
            "message": "Exception message"
        },
        "location": {
            "file": "filename",
            "line": X,
            "function": "function_name"
        },
        "timestamp": "YYYY-MM-DD HH:MM:SS",
        "input_context": {
            "user_input": user_input,
            "params": params
        },
        "traceback": traceback.format_exc(),
        "computer_info": {
            "OS": "OS name",
            "OS_version": "OS version",
            "Release": "OS release",
            "Architecture": "Machine architecture",
            "Processor": "Processor info",
            "Python_Version": "Python version",
            "Python_Executable": "Path to Python executable",
            "Current_Working_Directory": "Current working directory"
        }
    }
