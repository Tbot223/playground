# external Modules
from pathlib import Path
from typing import Union, List

# internal Modules
from CoreV2 import LogSys, FileManager, AppCore, Utils
from CoreV2.Result import Result
from CoreV2.Exception import ExceptionTrackerDecorator

class CountWord:
    """
    CountWord class provides functionality to count words in files and directories.
    
    Attributes:
        - BasePath (Union[str, Path]): Base path for the application. Defaults to the parent directory of the script.
        - is_logging_enabled (bool): Flag to enable or disable logging. Defaults to True.
        - logger (LogSys.Log): Logger instance for logging messages.
        - _log (LogSys.Log): Log instance for logging messages.
        - _file_manager (FileManager.FileManager): FileManager instance for file operations.
        - _app_core (AppCore.AppCore): AppCore instance for core application functionalities.
        - _utils (Utils.Utils): Utils instance for utility functions.

    Methods:
        - count_words_in_file(file_path: Union[str, Path]) -> Result:
            Count the number of words in a file.

        - files_word_count(file_paths: list[Union[str, Path]], workers: int = 1) -> Result:
            Count words in multiple files using multithreading.

        - count_words_in_directory(dir_path: Union[str, Path], extensions: List[str] = [".txt"], workers: int = 1) -> Result:
            Count words in all files with a specific extension within a directory.
    """
    def __init__(self, BasePath: Union[str, Path] = None, is_logging_enabled: bool = True,
                 logger_manager: LogSys.LoggerManager = None, log: LogSys.Log = None, file_manager: FileManager.FileManager = None,
                 app_core: AppCore.AppCore = None, utils: Utils.Utils = None):
        
        # Initialize Path
        self.BasePath = BasePath or Path(__file__).resolve().parent.parent

        # Initialize Flag
        self.is_logging_enabled = is_logging_enabled

        # Initialize classes
        self.logger = None
        if self.is_logging_enabled:
            self._logger_manager = logger_manager or LogSys.LoggerManager(base_dir=self.BasePath / "logs", second_log_dir="CountWordLogs")
            self._logger_manager.make_logger("CountWord")
            self.logger = self._logger_manager.get_logger("CountWord").data
        self._log = log or LogSys.Log(logger=self.logger)
        self._file_manager = file_manager or FileManager.FileManager(is_logging_enabled=False)
        self._app_core = app_core or AppCore.AppCore(is_logging_enabled=False)
        self._utils = utils or Utils.Utils(is_logging_enabled=False)

        self._log.log_message("INFO", "CountWord initialized.")

    @ExceptionTrackerDecorator()
    def count_words_in_file(self, file_path: Union[str, Path]) -> Result:
        """
        Count the number of words in a file.
        
        Args:
            - file_path : Path to the file.
            
        Returns:
            Result: A Result object containing the word count or an error message.
            
        Example:
            >>> count_word = CountWord()
            >>> result = count_word.count_words_in_file("example.txt")
            >>> if result.success:
            >>>     print(f"Word Count: {result.data}")
            >>> else:
            >>>     print(result.error)
        """
        file_path = self._utils.str_to_path(file_path).data
        content_result = self._file_manager.read_file(file_path=file_path)
        if not content_result.success:
            self._log.log_message("ERROR", f"Failed to read file: {file_path}. Error: {content_result.error}")
            return Result(False, content_result.error, f" Failed to read file: {file_path}", content_result.data)
        
        content = content_result.data
        word_count = len(content.split())
        self._log.log_message("INFO", f"Counted {word_count} words in file: {file_path}")
        return Result(True, None, f" Successfully counted words in file: {file_path}", word_count)
    
    @ExceptionTrackerDecorator()
    def files_word_count(self, file_paths: list[Union[str, Path]], workers: int = 1) -> Result:
        """
        Count words in multiple files using multithreading.

        Args:
            - file_paths : List of file paths to count words in.
            - workers : Number of worker threads to use (default is 1).

        Returns:
            Result: A Result object containing a list of word counts or an error message.
        Example:
            >>> count_word = CountWord()
            >>> result = count_word.files_word_count(["file1.txt", "file2.txt"], workers=4)
            >>> if result.success:
            >>>     for count in result.data:
            >>>         print(f"Word Count: {count}")
            >>> else:
            >>>     print(result.error)
        """
        tasks = [(self.count_words_in_file, {'file_path': path}) for path in file_paths]
        result = self._app_core.thread_pool_executor(data=tasks, workers=workers, override=True, timeout=0.2)
        self._log.log_message("INFO", f"Counted words in {len(file_paths)} files using {workers} workers.")
        return result
    
    @ExceptionTrackerDecorator()
    def count_words_in_directory(self, dir_path: Union[str, Path], extensions: List[str] = [".txt"], workers: int = 1) -> Result:
        """
        Count words in all files with a specific extension within a directory.
        
        Args:
            - directory_path : Path to the directory.
            - file_extension : File extension to filter files (default is ".txt").
            - workers : Number of worker threads to use (default is 1).
        Returns:
            Result: A Result object containing a dictionary of file paths and their word counts or an error message.
        
        Example:
            >>> count_word = CountWord()
            >>> result = count_word.count_words_in_directory("documents", [".txt"], workers=4)
            >>> if result.success:
            >>>     for file, count in result.data.items():
            >>>         print(f"{file}: {count} words")
            >>> else:
            >>>     print(result.error)
        """
        dir_path = self._utils.str_to_path(dir_path).data
        list_files_result = self._file_manager.list_of_files(dir_path=dir_path, extensions=extensions)
        if not list_files_result.success:
            self._log.log_message("ERROR", f"Failed to list files in directory: {dir_path}. Error: {list_files_result.error}")
            return Result(False, list_files_result.error, f" Failed to list files in directory: {dir_path}", list_files_result.data)
        
        file_paths = list_files_result.data
        word_count_result = self.files_word_count(file_paths=file_paths, workers=workers)
        if not word_count_result.success:
            self._log.log_message("ERROR", f"Failed to count words in files within directory: {dir_path}. Error: {word_count_result.error}")
            return Result(False, word_count_result.error, f" Failed to count words in files within directory: {dir_path}", word_count_result.data)
        
        word_counts = {str(file_paths[i]): word_count_result.data[i].data.data for i in range(len(file_paths))}
        self._log.log_message("INFO", f"Successfully counted words in directory: {dir_path}")
        return Result(True, None, f" Successfully counted words in directory: {dir_path}", word_counts)
    
if __name__ == "__main__":
    count_word = CountWord()
    print("""
 ██████  ██████  ██    ██ ███    ██ ████████     ██     ██  ██████  ██████  ██████  
██      ██    ██ ██    ██ ████   ██    ██        ██     ██ ██    ██ ██   ██ ██   ██ 
██      ██    ██ ██    ██ ██ ██  ██    ██        ██  █  ██ ██    ██ ██████  ██   ██ 
██      ██    ██ ██    ██ ██  ██ ██    ██        ██ ███ ██ ██    ██ ██   ██ ██   ██ 
 ██████  ██████   ██████  ██   ████    ██         ███ ███   ██████  ██   ██ ██████  
                                                                                   
""")
    print("Current working directory:", Path.cwd())
    dir = input("Enter directory path to count words in text files: ")
    if not dir:
        print("Directory path is required.")
        exit(1)
    extensions = []
    while True:
        ext = input("Enter file extension to filter (e.g., .txt), or 'done' to finish: ")
        if ext.lower() == 'done':
            break
        if not ext.startswith('.'):
            print("Please enter a valid file extension starting with a dot.")
            continue
        extensions.append(ext)
    workers = int(input("Enter number of workers to use: "))
    result = count_word.count_words_in_directory(dir_path=dir, extensions=extensions, workers=workers)
    if result.success:
        for file, count in result.data.items():
            print(f"{file}: {count} words")
    else:
        print(f"Error: {result.error}")