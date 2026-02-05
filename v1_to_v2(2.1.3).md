# V1 vs V2 (2.1.3) Differences / V1과 V2 (2.1.3)의 차이점

This document describes all differences between **V1 (legacy/Core)** and **V2 (tbot223_core 2.1.3)**.

이 문서는 **V1 (legacy/Core)**와 **V2 (tbot223_core 2.1.3)** 사이의 모든 차이점을 설명합니다.

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
12. [Added in V2 (2.1.3) / V2 (2.1.3)에서 추가됨](#12-added-in-v2-213--v2-213에서-추가됨)
13. [Summary Table / 요약표](#13-summary-table--요약표)

---

## 1. Overview / 개요

### V1 (legacy/Core)
- **Package name**: `Core`
- **Files**: 10 Python files
- **Total Lines**: ~2,500 lines
- **Scope**: Core + Application-specific modules (StorageManager)
- **Naming Style**: Mixed (camelCase + PascalCase + snake_case)
- **Dependencies**: Internal circular imports via `__init__.py`
- **Thread Safety**: None

### V2 (tbot223_core 2.1.3)
- **Package name**: `tbot223_core`
- **Files**: 7 Python files
- **Total Lines**: ~2,900 lines
- **Scope**: Pure core functionality only
- **Naming Style**: Consistent snake_case (PEP 8 compliant)
- **Dependencies**: Explicit module imports, no circular dependencies
- **Thread Safety**: `multiprocessing.RLock` in GlobalVars, Shared Memory support

---

## 2. Package Structure / 패키지 구조

### File Comparison / 파일 비교

| V1 (legacy/Core) | V2 (tbot223_core 2.1.3) | Status / 상태 | Lines V1 → V2 |
|------------------|-------------------------|---------------|---------------|
| `__init__.py` | `__init__.py` | Changed / 변경됨 | 9 → 0 (empty) |
| `AppCore.py` | `AppCore.py` | Rewritten / 재작성됨 | 222 → 534 |
| `DebugTool.py` | - | Removed / 제거됨 | 37 → 0 |
| `Deco.py` | - | Moved to Utils / Utils로 이동 | 27 → 0 |
| `Exception.py` | `Exception.py` | Extended / 확장됨 | 90 → 195 |
| `FileManager.py` | `FileManager.py` | Rewritten / 재작성됨 | 254 → 556 |
| `LogSys.py` | `LogSys.py` | Refactored / 리팩토링됨 | 127 → 268 |
| `ResultManager.py` | `Result.py` | Simplified / 간소화됨 | 52 → 26 |
| `StorageManager.py` | - | Removed / 제거됨 | 406 → 0 |
| `Utils.py` | `Utils.py` | Rewritten / 재작성됨 | 153 → 1,307 |

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

**V2 2.1.3 (empty file):**
```python
# (empty - explicit imports required)
```

### Directory Layout / 디렉토리 구조

**V1:**
```
legacy/
├── Core/
│   ├── __init__.py          # Exports 6 classes
│   ├── AppCore.py            # 222 lines
│   ├── DebugTool.py          # 37 lines
│   ├── Deco.py               # 27 lines
│   ├── Exception.py          # 90 lines
│   ├── FileManager.py        # 254 lines
│   ├── LogSys.py             # 127 lines
│   ├── ResultManager.py      # 52 lines
│   ├── StorageManager.py     # 406 lines
│   └── Utils.py              # 153 lines
├── language/                  # 언어 파일 (lowercase)
│   ├── en.json
│   └── ko.json
└── Test/
    ├── AppCore_test.py
    ├── log_test.py
    └── StorageManager_test.py
```

**V2 2.1.3:**
```
core/2.1.3/
├── tbot223_core/
│   ├── __init__.py           # Empty
│   ├── AppCore.py            # 534 lines
│   ├── Exception.py          # 195 lines
│   ├── FileManager.py        # 556 lines
│   ├── LogSys.py             # 268 lines
│   ├── Result.py             # 26 lines
│   ├── Utils.py              # 1,307 lines
│   └── __pycache__/
├── TEST/
└── (parent)/Languages/        # 언어 파일 (Capitalized, parent directory)
    ├── en.json
    └── ko.json
```

---

## 3. Module Import Style / 모듈 임포트 스타일

### V1 (Package-level imports)
```python
from Core import Result, ExceptionTracker, Deco, FileManager, GlobalVars, Intializer
from Core import LogSys as log
```

### V2 2.1.3 (Explicit module imports)
```python
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker, ExceptionTrackerDecorator
from tbot223_core.AppCore import AppCore, ResultWrapper
from tbot223_core.LogSys import LoggerManager, Log, SimpleSetting
from tbot223_core.Utils import Utils, DecoratorUtils, GlobalVars
from tbot223_core import FileManager
```

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Package name | `Core` | `tbot223_core` |
| `__init__.py` role | Exports 6 classes | Empty |
| Import style | `from Core import X` | `from tbot223_core.X import X` |
| Circular dependency risk | High | Low |

---

## 4. Naming Convention / 네이밍 컨벤션

### Method Names / 메서드명

| V1 | V2 2.1.3 | Change Type |
|----|----------|-------------|
| `Make_logger()` | `make_logger()` | PascalCase → snake_case |
| `Atomic_write()` | `atomic_write()` | PascalCase → snake_case |
| `getTextByLang()` | `get_text_by_lang()` | camelCase → snake_case |
| `log_msg()` | `log_message()` | Abbreviated → Full word |
| `count_run_time()` | `count_runtime()` | Underscore removed |
| `load_json()` | `read_json()` | Verb change (load → read) |
| `save_json()` | `write_json()` | Verb change (save → write) |
| `load_file()` | `read_file()` | Verb change (load → read) |

### Parameter Names / 파라미터명

| V1 | V2 2.1.3 | Logic Change |
|----|----------|--------------|
| `No_Log: bool` | `is_logging_enabled: bool` | Inverted logic |
| `isTest: bool` | - | Removed |
| `isDebug: bool` | `is_debug_enabled: bool` | Renamed |
| `json_data: Dict` | `dict_obj: Dict` | More generic |
| `nested_lookup: bool` | `nested: bool` | Shortened |
| `comparison_type: str` | `comparison: str` | Shortened |
| `parent_dir` | `base_dir` | Renamed |
| `logger_manager` | `logger_manager_instance` | More explicit |
| `log_class` | `log_instance` | More explicit |

### Internal Variable Names / 내부 변수명

| V1 | V2 2.1.3 |
|----|----------|
| `_base_dir` | `_BASE_DIR` |
| `_LOGGER_MANAGER` | `_logger_manager` |
| `LANGUAGE_DIR` | `_LANG_DIR` |
| `_LANG` | `_supported_langs` |
| - | `__is_logging_enabled__` (dunder style) |
| - | `__vars__`, `__lock__` (GlobalVars) |

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

**V2 2.1.3 (8 parameters):**
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

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Total parameters | 10 | 8 |
| `screen_clear_lines` | Configurable (default: 50) | Removed |
| `isTest` parameter | Available | Removed |
| `debug_tool` injection | Required | Removed |
| `default_lang` | Not available | Added (default: "en") |
| Logging flag | `No_Log` (True=disable) | `is_logging_enabled` (True=enable) |
| Initialization message | `print("Initializing...")` | Uses logger only (conditional) |
| Language directory | `language/` | `Languages/` |
| base_dir default | `Path(__file__).parent.parent` | `Path.cwd()` |

### `find_keys_by_value()` Comparison

**V1 (in AppCore):**
```python
def find_keys_by_value(self, json_data: Dict, threshold: Any, 
                       comparison_type: str, nested_lookup: bool = False):
    # comparison_type: "above", "below", "equal"
    # Operators: 3
```

**V2 2.1.3 (moved to Utils):**
```python
def find_keys_by_value(self, dict_obj: Dict, threshold: Union[int, float, str, bool],
                       comparison: str='eq', nested: bool=False,
                       separator: str="/", return_mod: str="flat") -> Result:
    # comparison: 'eq', 'ne', 'lt', 'le', 'gt', 'ge'
    # Operators: 6
    # New: separator, return_mod parameters
```

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Location | AppCore | Utils |
| Operators | 3 (`above`, `below`, `equal`) | 6 (`eq`, `ne`, `lt`, `le`, `gt`, `ge`) |
| `separator` param | None | Available |
| `return_mod` param | None | `flat`, `forest`, `path` |
| Nested key format | Dot notation only | Configurable separator |

### `getTextByLang()` → `get_text_by_lang()` Comparison

**V1:**
```python
def getTextByLang(self, lang: str, key: str) -> Result:
    if lang not in self._LANG:
        raise ValueError(f"Language '{lang}' is not supported.")
```

**V2 2.1.3:**
```python
@__lang_cache_management__
def get_text_by_lang(self, key: str, lang: str) -> Result:
    if lang not in self._supported_langs:
        lang = self._default_lang  # Fallback instead of error
```

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Method name | `getTextByLang` | `get_text_by_lang` |
| Parameter order | `(lang, key)` | `(key, lang)` |
| Unsupported language | Raises `ValueError` | Falls back to `default_lang` |
| Cache decorator | None | `@__lang_cache_management__` |
| Auto-reload on KeyError | No | Yes |

### `clear_screen()` → `clear_console()` Comparison

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Method name | `clear_screen` | `clear_console` |
| Return type | `None` | `Result` |
| Fallback on error | Print newlines | Return error Result |
| Newline count | `SCREEN_CLEAR_LINES` | No fallback |

### V2 2.1.3 Only Methods / V2 2.1.3 전용 메서드

#### `thread_pool_executor()` / `process_pool_executor()`
```python
def thread_pool_executor(self, data, workers=None, override=False, timeout=None) -> Result
def process_pool_executor(self, data, workers=None, override=False, timeout=None, chunk_size=None) -> Result
```

#### `safe_CLI_input()` (New in 2.1.3)
```python
def safe_CLI_input(self, prompt="", input_type=str, other_type=False,
                   valid_options=None, case_sensitive=False, 
                   allow_empty=False, max_retries=10) -> Result:
    """
    Safely get user input from CLI with validation and retry logic.
    """
```

#### `exit_application()` / `restart_application()`
```python
def exit_application(self, code=0, pause=False) -> Result
def restart_application(self, pause=False) -> Result
```

### V2 2.1.3 Only Classes in AppCore / AppCore 전용 클래스

#### `ResultWrapper` (New in 2.1.3)
```python
class ResultWrapper:
    """
    Decorator that wraps function return values in Result objects.
    Handles exceptions automatically.
    """
    @ResultWrapper()
    def my_function(x, y):
        return x + y
    
    result = my_function(5, 10)
    # Result(True, None, None, 15)
```

### V1 Only Methods / V1 전용 메서드

- `multi_process_executer()` - Replaced by `process_pool_executor()` in V2

---

## 6. FileManager

### Constructor Comparison / 생성자 비교

**V1 (9 parameters):**
```python
def __init__(self, isTest=False, isDebug=False, second_log_dir=None,
             logger=None, No_Log=False, LOG_DIR=None,
             log_class=None, logger_manager=None, debug_tool=None):
```

**V2 2.1.3 (7 parameters):**
```python
def __init__(self, is_logging_enabled=True, is_debug_enabled=False,
             base_dir=None, logger_manager_instance=None, logger=None,
             log_instance=None, Utils_instance=None):
```

### Class Constants (V2 2.1.3 Only)

```python
class FileManager:
    LOCK_FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
```

### Method Name Changes / 메서드명 변경

| V1 | V2 2.1.3 |
|----|----------|
| `load_json()` | `read_json()` |
| `save_json()` | `write_json()` |
| `Atomic_write()` | `atomic_write()` |
| `load_file()` | `read_file()` |

### `save_json()` → `write_json()` Detailed Comparison

**V1:**
```python
def save_json(self, data, file_path, key=None, serialization=False):
    # key: Update specific key only
    # serialization=True: Enable indent
```

**V2 2.1.3:**
```python
def write_json(self, file_path, data, indent=4):
    # Always overwrites entire file
    # Always pretty prints
```

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Parameter order | `(data, file_path)` | `(file_path, data)` |
| Key-based update | Supported | Not supported |
| Pretty print | Optional | Always enabled |
| Indent | Fixed at 4 | Configurable |

### File Locking (V2 2.1.3 Enhanced)

**V1:** None

**V2 2.1.3:**
```python
@staticmethod
def _lock(file, mode):
    """
    mode=1: Exclusive lock (LOCK_EX)
    mode=2: Shared lock (LOCK_SH) - NEW in 2.1.3
    mode=0: Unlock
    """
    if os.name != 'nt':  # Unix
        if mode == 1:
            fcntl.flock(file, fcntl.LOCK_EX)
        elif mode == 2:
            fcntl.flock(file, fcntl.LOCK_SH)  # New in 2.1.3
        else:
            fcntl.flock(file, fcntl.LOCK_UN)
    else:  # Windows
        if mode == 1:
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, size)
        else:
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, size)
```

### V2 2.1.3 Only Methods

```python
def list_of_files(self, dir_path, extensions=None, only_name=False) -> Result
def exist(self, path) -> Result
def delete_file(self, file_path) -> Result
def delete_directory(self, dir_path) -> Result
def create_directory(self, dir_path) -> Result
def __enter__(self)  # Context manager support
def __exit__(self, exc_type, exc_value, traceback)
```

### V1 Only Methods / V1 전용 메서드

- `load_json_threaded()` - Removed
- `write_json_threaded()` - Removed

---

## 7. LogSys

### LoggerManager Comparison / LoggerManager 비교

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Method name | `Make_logger()` | `make_logger()` |
| Log level param | Not available | `log_level: int` |
| Default log level | `DEBUG` (fixed) | `INFO` (configurable) |
| base_dir default | `__file__.parent.parent/logs` | `Path.cwd()/logs` |
| `second_log_dir` type | `str` | `Union[str, Path]` |
| `stop_stream_handlers()` | Not available | Available |

### Log Class Comparison / Log 클래스 비교

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Method name | `log_msg()` | `log_message()` |
| Logger param | Required | Optional |
| Level param type | `str` only | `Union[int, str]` |
| Level format | lowercase (`"info"`) | UPPERCASE or int |
| Supported levels | 4 | 5 (+ CRITICAL) |
| No-log mechanism | `no_log: bool` param | `logger=None` |

### V2 2.1.3 Only: `SimpleSetting` Class

```python
class SimpleSetting:
    """
    One-step initialization for LoggerManager, Logger, and Log.
    """
    def __init__(self, base_dir, second_log_dir, logger_name, log_level=logging.INFO):
        self.logger_manager = LoggerManager(base_dir, second_log_dir)
        self.logger_manager.make_logger(logger_name, log_level=log_level)
        self.logger = self.logger_manager.get_logger(logger_name).data
        self.log = Log(logger=self.logger)

# Usage
setting = SimpleSetting("logs", "app", "my_logger")
setting.log.log_message("INFO", "Hello!")
```

---

## 8. Exception

### ExceptionTracker Comparison / ExceptionTracker 비교

**V1:**
```python
def get_exception_info(self, error, user_input=None, params: dict=None):
    # params is dict
    "traceback": traceback.format_exc()
```

**V2 2.1.3:**
```python
def get_exception_info(self, error, user_input=None, 
                       params: Tuple[Tuple, dict]=None, masking=False):
    # params is (args, kwargs) tuple
    "traceback": ''.join(traceback.format_exception(type(error), error, error.__traceback__))
```

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Masking param | Not available | `masking: bool = False` |
| Computer info masking | Not available | Available |
| params type | `dict` | `Tuple[Tuple, dict]` |
| params format | `{"key": "value"}` | `((args), {kwargs})` |
| Traceback format | `format_exc()` | `format_exception()` |

### V2 Only: `get_exception_return()`

```python
def get_exception_return(self, error, user_input=None, 
                         params=None, masking=False) -> Result:
    """Convenience method for standardized exception returns."""
```

### V2 Only: `ExceptionTrackerDecorator`

```python
@ExceptionTrackerDecorator(masking=True)
def risky_function(x, y):
    return x / y

result = risky_function(10, 0)
# Result(False, 'ZeroDivisionError :division by zero', ...)
```

---

## 9. Result

### File Name Change / 파일명 변경

| V1 | V2 2.1.3 |
|----|----------|
| `ResultManager.py` (52 lines) | `Result.py` (26 lines) |

### Classes Comparison / 클래스 비교

| Class | V1 | V2 2.1.3 |
|-------|-----|----------|
| `Result` (NamedTuple) | ✅ | ✅ |
| `ExtendedResult` (dataclass) | ✅ | ❌ Removed |
| `ResultUtils` | ✅ | ❌ Removed |

---

## 10. Utils

### Complete Rewrite / 완전히 재작성됨

| Aspect | V1 | V2 2.1.3 |
|--------|-----|----------|
| Lines | 153 | 1,307 |
| Classes | 4 | 3 |
| Encryption | None | SHA, PBKDF2 |
| Shared Memory | None | Full support |
| Thread Safety | None | `RLock` |

### V1 Classes

```python
class Utils:
    def get_app_version(self) -> Tuple[str, str]
    def separation_line(self, length=50, char='-') -> str

class Intializer:
    """Bulk initialization of all components"""
    def initializer(self, logger_manager=None, logger_name="Initializer")

class GlobalVars:
    def set(self, key, value, overwrite=True) -> Result
    def get(self, key) -> Result
    def exists(self, key) -> Result
    def delete(self, key) -> Result
    def clear(self) -> Result

class ClassNameUpper(type):
    """Metaclass for uppercase class names"""
```

### V2 2.1.3 Classes

```python
class Utils:
    def str_to_path(self, path_str) -> Result
    def encrypt(self, data, algorithm='sha256') -> Result
    def pbkdf2_hmac(self, password, algorithm, iterations, salt_size) -> Result
    def verify_pbkdf2_hmac(self, password, salt_hex, hash_hex, iterations, algorithm) -> Result
    def insert_at_intervals(self, data, interval, insert, at_start=True) -> Result  # NEW in 2.1.3
    def find_keys_by_value(self, dict_obj, threshold, comparison, nested, separator, return_mod) -> Result  # Moved from AppCore

class DecoratorUtils:
    @staticmethod
    def count_runtime()
    def make_decorator(self, func)  # NEW in 2.1.3

class GlobalVars:
    # Basic methods
    def set(self, key, value, overwrite=False) -> Result
    def get(self, key) -> Result
    def delete(self, key) -> Result
    def clear(self) -> Result
    def list_vars(self) -> Result
    def exists(self, key) -> Result
    
    # Magic methods
    def __getattr__(self, name)
    def __setattr__(self, name, value)
    def __call__(self, key, value=None, overwrite=False) -> Result
    def __enter__(self)  # NEW in 2.1.3 - Context manager
    def __exit__(self, exc_type, exc_value, traceback)  # NEW in 2.1.3
    
    # Shared Memory (NEW in 2.1.3)
    def shm_gen(self, name=None, size=1024, create_lock=True) -> Result
    def shm_connect(self, name) -> Result
    def shm_get(self, name) -> Result
    def shm_close(self, name, close_only=False) -> Result
    def shm_update(self, name) -> Result
    def shm_sync(self, name) -> Result
    def lock(self) -> RLock
```

### GlobalVars Usage Comparison / GlobalVars 사용법 비교

**V1 (methods only):**
```python
globals = GlobalVars()
globals.set("api_key", "12345")
result = globals.get("api_key")
value = result.data
```

**V2 2.1.3 (multiple access patterns):**
```python
globals = GlobalVars()

# Pattern 1: Explicit methods
globals.set("api_key", "12345", overwrite=True)
result = globals.get("api_key")

# Pattern 2: Attribute access
globals.api_key = "12345"
value = globals.api_key

# Pattern 3: Call syntax
globals("api_key", "12345", overwrite=True)
result = globals("api_key")

# Pattern 4: Context manager (NEW in 2.1.3)
with globals:
    globals.set("key", "value", overwrite=True)
    value = globals.get("key")

# Pattern 5: Shared memory (NEW in 2.1.3)
globals.shm_gen("shared_data", size=4096)
globals.shm_sync("shared_data")  # Sync to shared memory
# In another process:
globals2.shm_connect("shared_data")
globals2.shm_update("shared_data")  # Load from shared memory
```

### DecoratorUtils Comparison

| Aspect | V1 (Deco) | V2 2.1.3 (DecoratorUtils) |
|--------|-----------|---------------------------|
| Location | `Deco.py` | `Utils.py` |
| Method name | `count_run_time()` | `count_runtime()` |
| Method type | Instance method | Static method |
| `make_decorator()` | None | Available |

---

## 11. Removed in V2 / V2에서 제거됨

### DebugTool.py (37 lines)

**Why removed:** Functionality merged into `is_debug_enabled` flag

### Deco.py (27 lines)

**Why removed:** Moved to `Utils.py` as `DecoratorUtils`

### StorageManager.py (406 lines)

**Why removed:** Application-specific, not core functionality

### Intializer Class

**Why removed:** V2 prefers explicit dependency injection

### ExtendedResult & ResultUtils

**Why removed:** Unnecessary complexity

### ClassNameUpper Metaclass

**Why removed:** Not commonly used

---

## 12. Added in V2 (2.1.3) / V2 (2.1.3)에서 추가됨

### Thread/Process Pool Executors
```python
app_core.thread_pool_executor(data, workers=4, timeout=10)
app_core.process_pool_executor(data, workers=4, chunk_size=10)
```

### Extended Comparison Operators
| V1 | V2 2.1.3 |
|----|----------|
| `"above"` | `'gt'` |
| `"below"` | `'lt'` |
| `"equal"` | `'eq'` |
| - | `'ne'`, `'le'`, `'ge'` |

### Cryptographic Utilities
```python
utils.encrypt("data", algorithm='sha256')
utils.pbkdf2_hmac("password", "sha256", 100000, 32)
utils.verify_pbkdf2_hmac("password", salt_hex, hash_hex, 100000, "sha256")
```

### Application Control
```python
app_core.exit_application(code=0, pause=True)
app_core.restart_application(pause=True)
```

### Platform-Specific File Locking
- Unix: `fcntl.flock()` with LOCK_EX and LOCK_SH
- Windows: `msvcrt.locking()`

### Exception Decorator
```python
@ExceptionTrackerDecorator(masking=True)
def risky_function(x, y):
    return x / y
```

### Context Manager Support
```python
with FileManager() as fm:
    content = fm.read_file("data.txt")

with GlobalVars() as gv:  # Thread-safe block
    gv.set("key", "value")
```

### safe_CLI_input() (NEW in 2.1.3)
```python
result = app_core.safe_CLI_input(
    prompt="Enter choice: ",
    valid_options=["yes", "no"],
    max_retries=3
)
```

### ResultWrapper Decorator (NEW in 2.1.3)
```python
@ResultWrapper()
def my_function(x):
    return x * 2
```

### SimpleSetting Class (NEW in 2.1.3)
```python
setting = SimpleSetting("logs", "app", "my_logger")
```

### Shared Memory IPC (NEW in 2.1.3)
```python
gv = GlobalVars()
gv.shm_gen("shared_vars", size=4096)
gv.shm_sync("shared_vars")  # Write to shared memory
# Another process:
gv2.shm_connect("shared_vars")
gv2.shm_update("shared_vars")  # Read from shared memory
```

### insert_at_intervals() (NEW in 2.1.3)
```python
utils.insert_at_intervals([1,2,3,4,5,6], interval=2, insert='X')
# Output: ['X', 1, 2, 'X', 3, 4, 'X', 5, 6]
```

### Language Cache Auto-Reload (NEW in 2.1.3)
```python
# @__lang_cache_management__ decorator handles KeyError by reloading
app_core.get_text_by_lang("key", "en")
```

---

## 13. Summary Table / 요약표

| Category | V1 | V2 2.1.3 |
|----------|-----|----------|
| Package name | `Core` | `tbot223_core` |
| Total files | 10 | 7 |
| Total lines | ~2,500 | ~2,900 |
| `__init__.py` | Exports 6 classes | Empty |
| Naming style | Mixed | snake_case |
| Language directory | `language/` | `Languages/` |
| DebugTool | Separate class | Removed |
| StorageManager | Included | Removed |
| Deco | Separate file | Moved to Utils |
| Result classes | 3 | 1 |
| Encryption | None | SHA, PBKDF2 |
| File locking | None | fcntl/msvcrt |
| Shared lock (LOCK_SH) | None | ✅ (Unix) |
| Comparison operators | 3 | 6 |
| GlobalVars access | Methods only | Methods + Attributes + Call |
| GlobalVars threading | None | `RLock` |
| GlobalVars shared memory | None | Full support |
| Context manager | None | FileManager, GlobalVars |
| Thread pool | None | `thread_pool_executor()` |
| Process pool | `multi_process_executer()` | `process_pool_executor()` |
| App control | None | `exit_application()`, `restart_application()` |
| Fallback language | None | `default_lang` parameter |
| Exception decorator | None | `ExceptionTrackerDecorator` |
| Result wrapper | None | `ResultWrapper` |
| Simple logging setup | None | `SimpleSetting` |
| CLI input validation | None | `safe_CLI_input()` |
| Log level config | Fixed (DEBUG) | Configurable |
| Logging disable | `No_Log=True` | `is_logging_enabled=False` |
| Conditional logging | None | `if __is_logging_enabled__:` |
| base_dir default | `__file__.parent.parent` | `Path.cwd()` |
| Workers default | None | `os.cpu_count()` |
| Serialization | None | pickle, json |
| IPC support | None | Shared memory |
