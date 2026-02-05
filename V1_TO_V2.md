# V1 vs V2 Differences / V1과 V2의 차이점

This document describes all differences between **V1 (legacy/Core)** and **V2 (tbot223_core 2.0.0)**.

이 문서는 **V1 (legacy/Core)**와 **V2 (tbot223_core 2.0.0)** 사이의 모든 차이점을 설명합니다.

---

## Table of Contents / 목차

1. [Overview / 개요](#1-overview--개요)
2. [Package Structure / 패키지 구조](#2-package-structure--패키지-구조)
3. [Module Import Style / 모듈 임포트 스타일](#3-module-import-style--모듈-임포트-스타일)
4. [Naming Convention / 네이밍 컨벤션](#4-naming-convention--네이밍-컨벤션)
5. [AppCore](#5-appcore)
6. [FileManager](#6-filemanager)
7. [LogSys](#7-logsys)
8. [Exception](#8-exception)
9. [Result](#9-result)
10. [Utils](#10-utils)
11. [Removed in V2 / V2에서 제거됨](#11-removed-in-v2--v2에서-제거됨)
12. [Added in V2 / V2에서 추가됨](#12-added-in-v2--v2에서-추가됨)
13. [Summary Table / 요약표](#13-summary-table--요약표)

---

## 1. Overview / 개요

### V1 (legacy/Core)
- **Package name**: `Core`
- **Files**: 10 Python files (222~406 lines each)
- **Total Lines**: ~2,500 lines
- **Scope**: Core + Application-specific modules (StorageManager)
- **Naming Style**: Mixed (camelCase + PascalCase + snake_case)
- **Dependencies**: Internal circular imports via `__init__.py`

### V2 (tbot223_core)
- **Package name**: `tbot223_core`
- **Files**: 7 Python files (183~614 lines each)
- **Total Lines**: ~2,400 lines
- **Scope**: Pure core functionality only
- **Naming Style**: Consistent snake_case (PEP 8 compliant)
- **Dependencies**: Explicit module imports, no circular dependencies

---

## 2. Package Structure / 패키지 구조

### File Comparison / 파일 비교

| V1 (legacy/Core) | V2 (tbot223_core) | Status / 상태 | Lines V1 → V2 |
|------------------|-------------------|---------------|---------------|
| `__init__.py` | `__init__.py` | Changed / 변경됨 | 9 → 0 (empty) |
| `AppCore.py` | `AppCore.py` | Rewritten / 재작성됨 | 222 → 445 |
| `DebugTool.py` | - | Removed / 제거됨 | 37 → 0 |
| `Deco.py` | - | Moved to Utils / Utils로 이동 | 27 → 0 |
| `Exception.py` | `Exception.py` | Extended / 확장됨 | 90 → 183 |
| `FileManager.py` | `FileManager.py` | Rewritten / 재작성됨 | 254 → 519 |
| `LogSys.py` | `LogSys.py` | Refactored / 리팩토링됨 | 127 → 176 |
| `ResultManager.py` | `Result.py` | Simplified / 간소화됨 | 52 → 26 |
| `StorageManager.py` | - | Removed / 제거됨 | 406 → 0 |
| `Utils.py` | `Utils.py` | Rewritten / 재작성됨 | 153 → 614 |

### `__init__.py` Comparison / `__init__.py` 비교

**V1 (9 lines - exports classes):**
```python
from .ResultManager import Result
from .Exception import ExceptionTracker
from .Deco import Deco
from .FileManager import FileManager
from .Utils import GlobalVars
from .Utils import Intializer

__all__ = ['Result', 'ExceptionTracker', 'Deco', 'FileManager', 'GlobalVars', 'Intializer']
```

**V2 (empty file):**
```python
# (empty - explicit imports required)
```

### Directory Layout / 디렉토리 구조

**V1:**
```
legacy/
├── Core/
│   ├── __init__.py
│   ├── AppCore.py
│   ├── DebugTool.py
│   ├── Deco.py
│   ├── Exception.py
│   ├── FileManager.py
│   ├── LogSys.py
│   ├── ResultManager.py
│   ├── StorageManager.py
│   └── Utils.py
├── language/              # 언어 파일 (lowercase)
│   ├── en.json
│   └── ko.json
└── Test/                  # 테스트 파일
    ├── AppCore_test.py
    ├── log_test.py
    └── StorageManager_test.py
```

**V2:**
```
tbot223_core/
├── __init__.py            # Empty
├── AppCore.py
├── Exception.py
├── FileManager.py
├── LogSys.py
├── Result.py
├── Utils.py
└── __pycache__/
(parent)/
└── Languages/             # 언어 파일 (Capitalized, parent directory)
    ├── en.json
    └── ko.json
```

---

## 3. Module Import Style / 모듈 임포트 스타일

### V1 (Package-level imports / 패키지 레벨 임포트)
```python
# Classes exported from __init__.py
from Core import Result, ExceptionTracker, Deco, FileManager, GlobalVars, Intializer
from Core import LogSys as log
from Core.Exception import ExceptionTracker

# Internal usage
from Core import Result, DebugTool, FileManager
from Core import LogSys as log
```

### V2 (Explicit module imports / 명시적 모듈 임포트)
```python
# Each class imported from its specific module
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core import FileManager, LogSys, Utils

# Internal usage
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core import FileManager, LogSys
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Package name / 패키지명 | `Core` | `tbot223_core` |
| `__init__.py` role | Exports 6 classes | Empty (no exports) |
| Import style | `from Core import X` | `from tbot223_core.X import X` |
| Circular dependency risk | High (via `__init__.py`) | Low (explicit imports) |

---

## 4. Naming Convention / 네이밍 컨벤션

### Method Names / 메서드명

| V1 | V2 | Change Type |
|----|----|-------------|
| `Make_logger()` | `make_logger()` | PascalCase → snake_case |
| `Atomic_write()` | `atomic_write()` | PascalCase → snake_case |
| `getTextByLang()` | `get_text_by_lang()` | camelCase → snake_case |
| `log_msg()` | `log_message()` | Abbreviated → Full word |
| `count_run_time()` | `count_runtime()` | Underscore removed |
| `load_json()` | `read_json()` | Verb change (load → read) |
| `save_json()` | `write_json()` | Verb change (save → write) |
| `load_file()` | `read_file()` | Verb change (load → read) |

### Parameter Names / 파라미터명

| V1 | V2 | Logic Change |
|----|----|--------------|
| `No_Log: bool` | `is_logging_enabled: bool` | Inverted (`True` = off → `True` = on) |
| `isTest: bool` | - | Removed |
| `isDebug: bool` | `is_debug_enabled: bool` | Renamed |
| `json_data: Dict` | `dict_obj: Dict` | More generic name |
| `nested_lookup: bool` | `nested: bool` | Shortened |
| `comparison_type: str` | `comparison: str` | Shortened |
| `parent_dir` | `base_dir` | Renamed |
| `logger_manager` | `logger_manager_instance` | More explicit |
| `log_class` | `log_instance` | More explicit |

### Internal Variable Names / 내부 변수명

| V1 | V2 |
|----|----|
| `_base_dir` | `_BASE_DIR` |
| `_LOGGER_MANAGER` | `_logger_manager` |
| `LANGUAGE_DIR` | `_LANG_DIR` |
| `_LANG` | `_supported_langs` |

---

## 5. AppCore

### Constructor Comparison / 생성자 비교

**V1 (10 parameters):**
```python
def __init__(self, 
             screen_clear_lines: int = 50,      # V2에서 제거됨
             parent_dir: Union[str, Path] = None,
             isTest: bool = False,              # V2에서 제거됨
             isDebug: bool = False, 
             logger = None, 
             No_Log: bool = False,              # 논리 반전됨
             filemanager: FileManager = None, 
             logger_manager: log.LoggerManager = None, 
             debug_tool: DebugTool.DebugTool = None,  # V2에서 제거됨
             log_class: log.Log = None):
```

**V2 (8 parameters):**
```python
def __init__(self, 
             is_logging_enabled: bool = True,   # No_Log의 반전 버전
             is_debug_enabled: bool = False, 
             default_lang: str = "en",          # 새로 추가됨
             base_dir: Union[str, Path] = None,
             logger_manager_instance: Optional[LogSys.LoggerManager] = None, 
             logger: Optional[logging.Logger] = None, 
             log_instance: Optional[LogSys.Log] = None, 
             filemanager: Optional[FileManager.FileManager] = None):
```

### Constructor Differences / 생성자 차이점

| Aspect | V1 | V2 |
|--------|-----|-----|
| Total parameters | 10 | 8 |
| `screen_clear_lines` | Configurable (default: 50) | Removed |
| `isTest` parameter | Available | Removed |
| `debug_tool` injection | Required | Removed |
| `default_lang` | Not available | Added (default: "en") |
| Logging flag | `No_Log` (True = disable) | `is_logging_enabled` (True = enable) |
| Initialization message | `print("Initializing AppCore...")` | Uses logger only |
| Language directory | `language/` (lowercase) | `Languages/` (capitalized) |
| Language detection | `os.listdir()` + manual filter | `FileManager.list_of_files()` |

### `find_keys_by_value()` Comparison

**V1:**
```python
def find_keys_by_value(self, json_data: Dict, threshold: Any, 
                       comparison_type: str, nested_lookup: bool = False) -> Result:
    """
    Args:
        comparison_type (str): "above", "below", "equal"
        threshold: Any (except dict, list, tuple)
    """
    compare_ops = {
        "above": lambda v: v > threshold,
        "below": lambda v: v < threshold,
        "equal": lambda v: v == threshold
    }
```

**V2:**
```python
def find_keys_by_value(self, dict_obj: Dict, threshold: Union[int, float, str, bool],  
                       comparison: str = 'eq', nested: bool = False) -> Result:
    """
    Args:
        comparison (str): 'eq', 'ne', 'lt', 'le', 'gt', 'ge'
        threshold: int, float, str, or bool only
    """
    comparison_operators = {
        'eq': lambda x: x == threshold,
        'ne': lambda x: x != threshold,
        'lt': lambda x: x < threshold,
        'le': lambda x: x <= threshold,
        'gt': lambda x: x > threshold,
        'ge': lambda x: x >= threshold,
    }
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| First param name | `json_data` | `dict_obj` |
| Comparison param name | `comparison_type` | `comparison` |
| Nested param name | `nested_lookup` | `nested` |
| Default comparison | None (required) | `'eq'` (optional) |
| Operators count | 3 | 6 |
| Operator names | `"above"`, `"below"`, `"equal"` | `'eq'`, `'ne'`, `'lt'`, `'le'`, `'gt'`, `'ge'` |
| Threshold types | Any (except collections) | `int`, `float`, `str`, `bool` only |
| Nested key output | Key only | Dot notation (`parent.child`) |

### `getTextByLang()` → `get_text_by_lang()` Comparison

**V1:**
```python
def getTextByLang(self, lang: str, key: str) -> Result:
    # Parameter order: lang first, then key
    # No fallback - raises error if lang not supported
    if lang not in self._LANG:
        raise ValueError(f"Language '{lang}' is not supported.")
```

**V2:**
```python
def get_text_by_lang(self, key: str, lang: str) -> Result:
    # Parameter order: key first, then lang
    # Fallback to default_lang if lang not supported
    if lang not in self._supported_langs:
        lang = self._default_lang
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Method name | `getTextByLang` | `get_text_by_lang` |
| Parameter order | `(lang, key)` | `(key, lang)` |
| Unsupported language | Raises `ValueError` | Falls back to `default_lang` |
| Cache variable | `_lang_cache` | `_lang_cache` (same) |

### `clear_screen()` → `clear_console()` Comparison

**V1:**
```python
def clear_screen(self):
    # Returns nothing (None)
    try:
        if os.name == 'nt':
            subprocess.run('cls', shell=True, check=True)
        else:
            subprocess.run('clear', shell=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('\n' * self.SCREEN_CLEAR_LINES)  # Fallback
```

**V2:**
```python
def clear_console(self) -> Result:
    # Returns Result object
    try:
        command = 'cls' if os.name == 'nt' else 'clear'
        subprocess.run(command, shell=True, check=True)
        return Result(True, None, None, "Console cleared successfully.")
    except Exception as e:
        return self._exception_tracker.get_exception_return(e)
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Method name | `clear_screen` | `clear_console` |
| Return type | `None` | `Result` |
| Fallback on error | Print newlines | Return error Result |
| Newline count | `SCREEN_CLEAR_LINES` (configurable) | No fallback |

### V2 Only Methods / V2 전용 메서드

#### `thread_pool_executor()`
```python
def thread_pool_executor(self, 
                         data: List[Tuple[Callable, Dict]], 
                         workers: int = None,           # Default: os.cpu_count() * 2
                         override: bool = False, 
                         timeout: float = None) -> Result:
    """
    Execute functions in parallel using ThreadPoolExecutor.
    Returns indexed list of Result objects.
    """
```

#### `process_pool_executor()`
```python
def process_pool_executor(self, 
                          data: List[Tuple[Callable, Dict]], 
                          workers: int = None,          # Default: os.cpu_count() * 2
                          override: bool = False, 
                          timeout: float = None,
                          chunk_size: Optional[int] = None) -> Result:
    """
    Execute functions in parallel using ProcessPoolExecutor.
    Supports chunking for large datasets.
    """
```

#### `exit_application()`
```python
def exit_application(self, code: int = 0, pause: bool = False) -> Result:
    """
    Exit application with specified code.
    If pause=True, waits for Enter key before exiting.
    Returns only on failure.
    """
```

#### `restart_application()`
```python
def restart_application(self, pause: bool = False) -> Result:
    """
    Restart the current Python application.
    Uses os.execl() to replace current process.
    Returns only on failure.
    """
```

### V1 Only Methods / V1 전용 메서드

#### `multi_process_executer()` (Replaced by `process_pool_executor` in V2)
```python
def multi_process_executer(self, 
                           tasks: List[Tuple[Callable, Dict]], 
                           process: int = 2, 
                           overprocess: bool = False) -> Result:
    # Limit: process * 4 CPU count
    # No timeout support
    # No chunking support
```

---

## 6. FileManager

### Constructor Comparison / 생성자 비교

**V1 (9 parameters):**
```python
def __init__(self, 
             isTest: bool = False, 
             isDebug: bool = False, 
             second_log_dir: Union[str, Path] = None,
             logger = None, 
             No_Log: bool = False, 
             LOG_DIR: str = None,
             log_class: log.Log = None, 
             logger_manager: log.LoggerManager = None, 
             debug_tool: DebugTool.DebugTool = None):
```

**V2 (7 parameters):**
```python
def __init__(self, 
             is_logging_enabled: bool = True, 
             is_debug_enabled: bool = False,
             base_dir: Union[str, Path] = None,
             logger_manager_instance: Optional[LogSys.LoggerManager] = None, 
             logger: Optional[logging.Logger] = None, 
             log_instance: Optional[LogSys.Log] = None, 
             Utils_instance: Optional[Utils.Utils] = None):  # New: Utils injection
```

### Method Comparison / 메서드 비교

| V1 Method | V2 Method | Signature Change |
|-----------|-----------|------------------|
| `load_json(file_path)` | `read_json(file_path)` | Name only |
| `save_json(data, file_path, key, serialization)` | `write_json(file_path, data, indent=4)` | Simplified API |
| `Atomic_write(data, file_path, No_log)` | `atomic_write(file_path, data)` | Param order reversed, No_log removed |
| `load_file(file_path)` | `read_file(file_path, as_bytes=False)` | Added `as_bytes` option |
| `load_json_threaded(file_paths, workers)` | - | Removed |
| `write_json_threaded(data_list, batch_size, base_path, workers)` | - | Removed |

### `save_json()` → `write_json()` Detailed Comparison

**V1:**
```python
def save_json(self, data: dict, file_path: str, 
              key: str = None,              # Update specific key
              serialization: bool = False)  # Pretty print
    # If key is provided, merges with existing JSON
    # serialization=True adds indent=4
```

**V2:**
```python
def write_json(self, file_path: Union[str, Path], 
               data: Any, 
               indent: int = 4)  # Always pretty prints
    # Always overwrites entire file
    # No key-based merge feature
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Parameter order | `(data, file_path)` | `(file_path, data)` |
| Key-based update | Supported (`key` param) | Not supported |
| Pretty print | Optional (`serialization=True`) | Always enabled (`indent=4`) |
| Indent value | Fixed at 4 when enabled | Configurable |

### `Atomic_write()` → `atomic_write()` Detailed Comparison

**V1:**
```python
def Atomic_write(self, data: Any, file_path: Union[str, Path], 
                 No_log: bool = False) -> Result:
    # Uses tempfile.NamedTemporaryFile
    # No file locking
```

**V2:**
```python
def atomic_write(self, file_path: Union[str, Path], 
                 data: Any) -> Result:
    # Uses tempfile.NamedTemporaryFile
    # Adds file locking via _lock() method
    # Supports both text and binary modes
    # Calls os.fsync() for data integrity
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Parameter order | `(data, file_path)` | `(file_path, data)` |
| File locking | None | Platform-specific (fcntl/msvcrt) |
| Data sync | None | `os.fsync()` |
| Binary support | Text only | Text and binary (`isinstance(data, bytes)`) |

### V2 Only Methods / V2 전용 메서드

```python
def list_of_files(self, dir_path, extensions=None, only_name=False) -> Result:
    """List files in directory with optional extension filter."""

def exist(self, path) -> Result:
    """Check if file or directory exists."""

def delete_file(self, file_path) -> Result:
    """Delete a file with permission handling."""

def delete_directory(self, dir_path) -> Result:
    """Delete directory recursively with permission handling."""

def create_directory(self, dir_path) -> Result:
    """Create directory with parents."""

# Context Manager support
def __enter__(self): return self
def __exit__(self, exc_type, exc_value, traceback): pass
```

### File Locking (V2 Only) / 파일 잠금 (V2 전용)

```python
@staticmethod
def _lock(file: Path, mode: int):
    """
    Lock a file.
    - mode=1: Lock (LOCK_EX on Unix, LK_LOCK on Windows)
    - mode=0: Unlock
    """
    if os.name != 'nt':  # Unix
        fcntl.flock(file, fcntl.LOCK_EX if mode == 1 else fcntl.LOCK_UN)
    else:  # Windows
        if mode == 1:
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, os.path.getsize(file.name))
        else:
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, os.path.getsize(file.name))
```

---

## 7. LogSys

### LoggerManager Comparison / LoggerManager 비교

**V1:**
```python
class LoggerManager:
    def __init__(self, base_dir=None, second_log_dir="default"):
        self._base_dir = base_dir  # lowercase
        
    def Make_logger(self, name="TEST", time=None) -> Result:
        # Fixed log level: DEBUG
        logger.setLevel(logging.DEBUG)
        return Result(True, None, None, True)
```

**V2:**
```python
class LoggerManager:
    def __init__(self, base_dir=None, second_log_dir="default"):
        self._BASE_DIR = base_dir  # UPPERCASE
        
    def make_logger(self, logger_name: str, 
                    log_level: int = logging.INFO,  # Configurable
                    time: Any = None) -> Result:
        logger.setLevel(log_level)
        return Result(True, None, None, f"Logger '{logger_name}' created successfully.")
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Method name | `Make_logger()` | `make_logger()` |
| First param name | `name` | `logger_name` |
| Default log level | `DEBUG` (fixed) | `INFO` (configurable) |
| Log level param | Not available | `log_level: int` |
| Return data | `True` | `"Logger 'name' created successfully."` |
| Internal var | `_base_dir` | `_BASE_DIR` |

### Log Class Comparison / Log 클래스 비교

**V1:**
```python
class Log:
    def __init__(self, logger: logging.Logger):
        self.log_levels = {
            "info": self.logger.info,
            "error": self.logger.error,
            "debug": self.logger.debug,
            "warning": self.logger.warning
        }

    def log_msg(self, level: str, message: str, no_log: bool = False):
        # level must be lowercase string
        # no_log=True disables logging
```

**V2:**
```python
class Log:
    def __init__(self, logger: logging.Logger = None):  # Optional logger
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

    def log_message(self, level: Optional[Union[int, str]], message: str):
        # level can be string ("INFO") or int (logging.INFO)
        # No no_log param - use logger=None instead
        if self.logger is None:
            return Result(False, None, None, "Logger is not initialized.")
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Method name | `log_msg()` | `log_message()` |
| Logger param | Required | Optional (can be `None`) |
| Level param type | `str` only | `Union[int, str]` |
| Level format | lowercase (`"info"`) | UPPERCASE (`"INFO"`) or int |
| Supported levels | 4 (info, error, debug, warning) | 5 (+ CRITICAL) |
| No-log mechanism | `no_log: bool` param | `logger=None` |

---

## 8. Exception

### ExceptionTracker Comparison / ExceptionTracker 비교

**V1:**
```python
class ExceptionTracker:
    def get_exception_info(self, error: Exception, 
                           user_input: Any = None, 
                           params: dict = None) -> Result:
        # No masking option
        error_info = {
            ...
            "computer_info": self._system_info  # Always exposed
        }
```

**V2:**
```python
class ExceptionTracker:
    def get_exception_info(self, error: Exception, 
                           user_input: Any = None, 
                           params: dict = None,
                           masking: bool = False) -> Result:  # New param
        error_info = {
            ...
            "computer_info": self._system_info if not masking else "<Masked>"
        }
```

| Aspect | V1 | V2 |
|--------|-----|-----|
| Masking param | Not available | `masking: bool = False` |
| Computer info | Always exposed | Can be masked with `<Masked>` |

### V2 Only: `get_exception_return()`

```python
def get_exception_return(self, error: Exception, 
                         user_input: Any = None, 
                         params: dict = None, 
                         masking: bool = False) -> Result:
    """
    Convenience method for standardized exception returns.
    Combines get_exception_location() and get_exception_info().
    
    Returns:
        Result(False, 
               f"{type(error).__name__} :{str(error)}", 
               location_string, 
               exception_info or "<Masked>")
    """
```

### V2 Only: `ExceptionTrackerDecorator`

```python
class ExceptionTrackerDecorator:
    """
    Decorator for automatic exception tracking.
    
    Usage:
        @ExceptionTrackerDecorator(masking=True)
        def risky_function(x, y):
            return x / y
    
    On exception, returns Result object instead of raising.
    """
    def __init__(self, masking: bool = False, tracker: ExceptionTracker = None):
        self.tracker = tracker or ExceptionTracker()
        self.masking = masking

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return self.tracker.get_exception_return(
                    error=e, params=kwargs, masking=self.masking
                )
        return wrapper
```

---

## 9. Result

### File Name Change / 파일명 변경

| V1 | V2 |
|----|-----|
| `ResultManager.py` (52 lines) | `Result.py` (26 lines) |

### Classes Comparison / 클래스 비교

**V1 (3 classes):**
```python
from typing import NamedTuple, Optional, Any, Union
from dataclasses import dataclass

class Result(NamedTuple):
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any

@dataclass
class ExtendedResult:
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any

class ResultUtils:
    @staticmethod
    def is_success(result: Union[Result, ExtendedResult]) -> bool: ...
    
    @staticmethod
    def to_extended(result: Result) -> ExtendedResult: ...
    
    @staticmethod
    def to_named_tuple(result: ExtendedResult) -> Result: ...
```

**V2 (1 class):**
```python
from typing import Any, NamedTuple, Optional

class Result(NamedTuple):
    """
    Class representing operation results in CoreV2
    NamedTuple version
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any

# Note in V2:
# "Avoid using ExtendedResult or ResultUtils in CoreV2 for now, 
# as dataclass features or conversion utilities are not currently needed."
```

| Class | V1 | V2 | Notes |
|-------|-----|-----|-------|
| `Result` | ✅ | ✅ | Same structure |
| `ExtendedResult` | ✅ | ❌ | Removed |
| `ResultUtils` | ✅ | ❌ | Removed |

---

## 10. Utils

### Complete Rewrite / 완전히 재작성됨

### V1 Classes and Methods

```python
class Utils:
    def get_app_version(self) -> Tuple[str, str]:
        return "0.0.1", "Alpha"
    
    def separation_line(self, length: int = 50, char: str = '-') -> str:
        return char * length

class Intializer:
    """Initialize all core components at once"""
    def initializer(self, logger_manager=None, logger_name="Initializer"):
        self.LoggerManager = ...
        self.Log = ...
        self.AppCore = ...
        self.GlobalVars = ...
        self.FileManager = ...
        self.Deco = ...
        self.ExceptionTracker = ...
        self.DebugTool = ...
        self.ResultManager = ...

class GlobalVars:
    def set(self, key: str, value: Any, overwrite: bool = True) -> Result: ...
    def exists(self, key: str) -> Result: ...
    def get(self, key: str) -> Result: ...
    def delete(self, key: str) -> Result: ...
    def clear(self) -> Result: ...

class ClassNameUpper(type):
    """Metaclass to convert class names to uppercase"""
```

### V2 Classes and Methods

```python
class Utils:
    def __init__(self, is_logging_enabled=False, base_dir=None, ...): ...
    
    def str_to_path(self, path_str: str) -> Result:
        """Convert string to Path object"""
    
    def encrypt(self, data: str, algorithm: str = 'sha256') -> Result:
        """
        Encrypt string using hash algorithm.
        Supported: 'md5', 'sha1', 'sha256', 'sha512'
        """
    
    def pbkdf2_hmac(self, password: str, algorithm: str, 
                   iterations: int, salt_size: int) -> Result:
        """
        Generate PBKDF2 HMAC hash.
        Returns: {salt_hex, hash_hex, iterations, algorithm}
        """
    
    def verify_pbkdf2_hmac(self, password: str, salt_hex: str, 
                          hash_hex: str, iterations: int, 
                          algorithm: str) -> Result:
        """Verify PBKDF2 HMAC hash. Returns bool."""

class DecoratorUtils:
    @staticmethod
    def count_runtime():
        """Decorator to measure execution time"""

class GlobalVars:
    def __init__(self, is_logging_enabled=False, ...): ...
    
    # Explicit methods (same as V1)
    def set(self, key: str, value: object, overwrite: bool = False) -> Result: ...
    def get(self, key: str) -> Result: ...
    def delete(self, key: str) -> Result: ...
    def clear(self) -> Result: ...
    def exists(self, key: str) -> Result: ...
    
    # New in V2
    def list_vars(self) -> Result:
        """List all variable names"""
    
    # Magic methods (V2 only)
    def __getattr__(self, name):
        """Access via globals.key"""
    
    def __setattr__(self, name, value):
        """Set via globals.key = value"""
    
    def __call__(self, key: str, value=None, overwrite: bool = False) -> Result:
        """Access via globals("key") or globals("key", "value")"""
```

### GlobalVars Usage Comparison / GlobalVars 사용법 비교

**V1 (methods only):**
```python
globals = GlobalVars()
globals.set("api_key", "12345")
result = globals.get("api_key")
value = result.data  # "12345"
```

**V2 (three access patterns):**
```python
globals = GlobalVars()

# Pattern 1: Explicit methods
globals.set("api_key", "12345", overwrite=True)
result = globals.get("api_key")

# Pattern 2: Attribute access
globals.api_key = "12345"
value = globals.api_key  # "12345"

# Pattern 3: Call syntax
globals("api_key", "12345", overwrite=True)
result = globals("api_key")
```

### DecoratorUtils (Replaces V1 Deco.py)

**V1 (Deco.py - Instance method):**
```python
class Deco:
    def count_run_time(self):  # Instance method
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                print(f"This ran for {time.time() - start_time:.4f} seconds.")
                return result
            return wrapper
        return decorator

# Usage
deco = Deco()
@deco.count_run_time()
def my_function(): ...
```

**V2 (Utils.py - Static method):**
```python
class DecoratorUtils:
    @staticmethod
    def count_runtime():  # Static method
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                print(f"This ran for {time.time() - start_time:.4f} seconds.")
                return result
            return wrapper
        return decorator

# Usage
@DecoratorUtils.count_runtime()
def my_function(): ...
```

| Aspect | V1 (Deco) | V2 (DecoratorUtils) |
|--------|-----------|---------------------|
| Location | `Deco.py` (separate file) | `Utils.py` (integrated) |
| Method name | `count_run_time()` | `count_runtime()` |
| Method type | Instance method | Static method |
| Requires instance | Yes (`Deco()`) | No |

---

## 11. Removed in V2 / V2에서 제거됨

### DebugTool.py (37 lines)

**V1 Code:**
```python
class DebugTool:
    def __init__(self, logger):
        self.logger = logger

    def debug_log(self, message: str, isDebug: bool):
        if isDebug:
            self.logger.debug(message)
            return Result(True, None, None, True)
        return Result(True, None, "Debug is disabled", False)
```

**Why removed:** 
- Functionality merged into logging system
- V2 classes use `is_debug_enabled` flag directly
- Reduces unnecessary abstraction layer

### Deco.py (27 lines)

**V1 Code:**
```python
class Deco:
    def count_run_time(self):
        def decorator(func):
            ...
```

**Why removed:**
- Moved to `Utils.py` as `DecoratorUtils` class
- Changed from instance method to static method
- Consolidates utility functionality

### StorageManager.py (406 lines)

**V1 Features:**
- `load_data()` - Load JSON data by type
- `save_data()` - Save JSON data by type
- `save_all()` - Save multiple data types
- `save_metadata()` / `load_metadata()` - Metadata handling
- `list_saves()` - List all saves
- `delete_save()` - Delete save folder
- `save_exists()` - Check save existence
- `validate_save()` - Validate required files
- `get_latest_save_id()` - Get most recent save

**Why removed:**
- Application-specific, not core functionality
- Can be reimplemented using V2 FileManager methods:
  - `read_json()`, `write_json()`
  - `list_of_files()`, `exist()`
  - `delete_directory()`, `create_directory()`

### Intializer Class (in Utils.py)

**V1 Code:**
```python
class Intializer:
    def initializer(self, logger_manager=None, logger_name="Initializer"):
        self.LoggerManager = ...
        self.Log = ...
        self.AppCore = ...
        # ... all components initialized at once
```

**Why removed:**
- V2 prefers explicit dependency injection
- Each class manages its own dependencies
- More flexible and testable architecture

### ExtendedResult & ResultUtils (in ResultManager.py)

**Why removed:**
- `ExtendedResult` (dataclass): Not needed, `Result` (NamedTuple) sufficient
- `ResultUtils`: Conversion utilities unnecessary for current use cases
- Simplifies codebase without losing functionality

---

## 12. Added in V2 / V2에서 추가됨

### Thread/Process Pool Executors (AppCore)

```python
# ThreadPoolExecutor - for I/O-bound tasks
data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
result = app_core.thread_pool_executor(
    data=data,
    workers=4,              # Default: os.cpu_count() * 2
    override=False,         # Allow workers > tasks
    timeout=10.0            # Per-task timeout (seconds)
)
# Returns: Result with list of Results for each task

# ProcessPoolExecutor - for CPU-bound tasks
result = app_core.process_pool_executor(
    data=data,
    workers=4,
    override=False,
    timeout=10.0,
    chunk_size=10           # Split large datasets
)
```

### Extended Comparison Operators (AppCore)

| V1 Operator | V2 Operator | Python Equivalent |
|-------------|-------------|-------------------|
| `"above"` | `'gt'` | `>` |
| `"below"` | `'lt'` | `<` |
| `"equal"` | `'eq'` | `==` |
| - | `'ne'` | `!=` |
| - | `'le'` | `<=` |
| - | `'ge'` | `>=` |

### Cryptographic Utilities (Utils)

```python
utils = Utils()

# Simple hash (one-way encryption)
result = utils.encrypt("my_data", algorithm='sha256')
# Supported: 'md5', 'sha1', 'sha256', 'sha512'
# Returns: hex string

# PBKDF2 HMAC (password hashing)
hash_result = utils.pbkdf2_hmac(
    password="my_password",
    algorithm="sha256",     # 'sha1', 'sha256', 'sha512'
    iterations=100000,
    salt_size=32
)
# Returns: {salt_hex, hash_hex, iterations, algorithm}

# Verify password
verify_result = utils.verify_pbkdf2_hmac(
    password="my_password",
    salt_hex=hash_result.data["salt_hex"],
    hash_hex=hash_result.data["hash_hex"],
    iterations=100000,
    algorithm="sha256"
)
# Returns: bool (True if match)
```

### Application Control (AppCore)

```python
# Exit application
app_core.exit_application(
    code=0,         # Exit code (default: 0)
    pause=True      # Wait for Enter before exit
)

# Restart application
app_core.restart_application(
    pause=True      # Wait for Enter before restart
)
```

### Platform-Specific File Locking (FileManager)

```python
# Automatic locking in atomic_write()
# Files > 10MB are locked during read_file()

# Internal implementation:
if os.name != 'nt':  # Unix/Linux/macOS
    import fcntl
    fcntl.flock(file, fcntl.LOCK_EX)  # Exclusive lock
else:  # Windows
    import msvcrt
    msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, size)
```

### Exception Decorator (Exception)

```python
from tbot223_core.Exception import ExceptionTrackerDecorator

@ExceptionTrackerDecorator(masking=True)
def divide(a, b):
    return a / b

result = divide(10, 0)
# Instead of raising ZeroDivisionError, returns:
# Result(False, 'ZeroDivisionError :division by zero', 
#        "'file.py', line X, in divide", '<Masked>')
```

### Context Manager Support (FileManager)

```python
# V2 FileManager supports 'with' statement
with FileManager() as fm:
    content = fm.read_file("data.txt")
    fm.write_json("output.json", {"key": "value"})
# Automatic cleanup (if any) on exit
```

### Fallback Language (AppCore)

```python
# V2 supports default language fallback
app_core = AppCore(default_lang="en")

# If "fr" is not supported, falls back to "en"
result = app_core.get_text_by_lang("greeting", "fr")
# Returns text from "en" if "fr" not available
```

---

## 13. Summary Table / 요약표

| Category | V1 | V2 |
|----------|-----|-----|
| Package name | `Core` | `tbot223_core` |
| Total files | 10 | 7 |
| Total lines | ~2,500 | ~2,400 |
| `__init__.py` | Exports 6 classes | Empty |
| Naming style | Mixed (camelCase, PascalCase, snake_case) | Consistent snake_case |
| Language directory | `language/` (lowercase) | `Languages/` (capitalized) |
| DebugTool | Separate class (`DebugTool.py`) | Removed (integrated) |
| StorageManager | Included (`StorageManager.py`) | Removed |
| Deco | Separate file (`Deco.py`) | Moved to `Utils.py` as `DecoratorUtils` |
| Result classes | 3 (`Result`, `ExtendedResult`, `ResultUtils`) | 1 (`Result` only) |
| Encryption | None | SHA-family, PBKDF2 HMAC |
| File locking | None | Platform-specific (fcntl/msvcrt) |
| Comparison operators | 3 (`above`, `below`, `equal`) | 6 (`eq`, `ne`, `lt`, `le`, `gt`, `ge`) |
| GlobalVars access | Methods only | Methods + Attributes + Call |
| Thread pool | Not available | `thread_pool_executor()` |
| Process pool | `multi_process_executer()` | `process_pool_executor()` (with chunking) |
| App control | Not available | `exit_application()`, `restart_application()` |
| Fallback language | Not available | `default_lang` parameter |
| Context manager | Not available | FileManager supports `with` statement |
| Exception decorator | Not available | `ExceptionTrackerDecorator` |
| Log level config | Fixed (DEBUG) | Configurable |
| Logging disable | `No_Log=True` | `is_logging_enabled=False` |


