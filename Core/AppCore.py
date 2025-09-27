# external modules
import json
import os
import tempfile
import shutil
import subprocess
import traceback
import time
from typing import NamedTuple
from typing import Any, Dict, List, Tuple, Union, Optional

# internal modules
import Result

class AppCore:
    """
    AppCore 클래스는 통합적으로 여러 프로그램의 핵심 시스템 기능을 제공합니다.

    JSON 파일 관리, 다국어 지원, 자료 구조 검색 등 
    대부분의 프로그램에 적용 가능한 핵심 시스템 기능을 제공합니다.

    1. 다국어 지원: 여러 언어로 된 텍스트를 관리하고 반환하는 기능을 제공합니다.
        - text: 언어 설정에 따라 텍스트를 반환합니다.

    2. 자료 구조 검색: 딕셔너리에서 특정 조건을 만족하는 키를 찾는 기능을 제공합니다.
        - find_keys_by_value: 딕셔너리에서 특정 값 이상을 가진 키들을 찾습니다.

    3. 화면 지우기: 플랫폼 독립적으로 화면을 지우는 기능을 제공합니다.
        - clear_screen: 화면을 지웁니다.

    4. 예외 위치 추적: 예외가 발생한 위치를 추적하고 관련 정보를 반환하는 기능을 제공합니다.
        - get_exception_location: 예외가 발생한 위치를 반환합니다.
    """
    SCREEN_CLEAR_LINES = 50  # 매직 넘버를 상수로

    def __init__(self):
        os.makedirs("language", exist_ok=True)
        self.lang = [os.path.splitext(file)[0] for file in os.listdir("./language")]
        self._lang_cache = {}  # 언어 캐시 딕셔너리
        self.FileManager = FileManager()
        self.exception_tracker = ExceptionTracker()

    def find_keys_by_value(self, json_data: Dict, threshold: Any, comparison_type: str) -> Result:
        """
        딕셔너리에서 특정 값 이상을 가진 키들을 찾는 함수

        만약 글자일 경우 equal만 지원합니다.
        (bit 비교 지원 예정)

        Args:
            comparison_type (str): 비교 유형 ("above", "below", "equal")
            threshold (int or float): 기준 값 (equal의 경우 Any)
            json_data (dict): 딕셔너리 데이터

        Returns:
            tuple: (bool, str or None, str or None, list or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (list or dict)
        """
        try:
            matching_keys = []
            comparison_type = comparison_type.lower()

            if comparison_type == "above": # 초과
                for key, value in json_data.items(): # dict 순회
                    if value > threshold: # > 비교
                        matching_keys.append(key)
                return True, None, None, matching_keys
            elif comparison_type == "below": # 미만
                for key, value in json_data.items():
                    if value < threshold:
                        matching_keys.append(key)
                return True, None, None, matching_keys
            elif comparison_type == "equal": # 동일
                for key, value in json_data.items():
                    if value == threshold:
                        matching_keys.append(key)
                return Result(True, None, None, matching_keys)
            else:
                raise ValueError("Invalid comparison_type. Use 'above', 'below', or 'equal'.")
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def text(self, lang: str, key: str) -> Result:
        """
        언어 설정에 따라 텍스트를 반환하는 함수

        Fallback 메커니즘이 없습니다.
        호출 전에 언어와 키가 유효한지 확인해야 합니다.
        실패 시 캐시 초기화 및 예외 처리합니다.

        Args:
            lang (str): 언어 설정
            key (str): 텍스트 키
        Returns:
            tuple: (bool, str or None, str or None, str or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (str or dict)
        """
        try:
            if lang not in self.lang: # 언어 확인
                raise ValueError(f"Language '{lang}' not supported. Available languages: {self.lang}")

            # 캐시 확인
            if lang not in self._lang_cache:
                cache = self.FileManager.load_json(f"./language/{lang}.json")
                if not cache.success:
                    raise FileNotFoundError(f"Language file for '{lang}' could not be loaded.")
                self._lang_cache[lang] = cache.data

            # 텍스트 반환
            if key in self._lang_cache[lang]:
                return Result(True, None, None, self._lang_cache[lang][key])
            else:
                raise KeyError(f"Key '{key}' not found in language '{lang}'. Available keys: {list(self._lang_cache[lang].keys())}")
        except Exception as e:
            self._lang_cache = {}  # 캐시 초기화
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def clear_screen(self):
        """
        화면을 지우는 함수
        플랫폼 독립적이고 안전한 방법을 사용합니다.

        - Returns is not necessary as this function does not return any value.
        - This function clears the console screen.
        """
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.run('cls', shell=True, check=True)
            else:  # Unix/Linux/macOS
                subprocess.run('clear', shell=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 명령어 실행 실패 시 대체
            print('\n' * self.SCREEN_CLEAR_LINES)

class FileManager():
    """
    FileManager 클래스는 다양한 파일 형식을 읽고 쓰는 기능을 제공합니다.

    현재는 JSON 파일 형식만 지원하지만, 향후 다른 형식도 추가할 수 있습니다.

    1. JSON 파일 관리: JSON 파일을 안전하게 읽고 쓰는 기능을 제공합니다.
        - load_json: JSON 파일을 딕셔너리로 불러옵니다.
        - save_json: 딕셔너리를 JSON 파일로 저장합니다. (원자적 쓰기 적용)

    2. 원자적 쓰기: 파일 저장 시 데이터 손상을 방지하기 위해 임시 파일을 사용하여 안전하게 저장합니다.
    """
    def __init__(self):
        self.exception_tracker = ExceptionTracker()

    def load_json(self, file_path: str) -> Result:
        """
        json 파일을 딕셔너리로 불러오는 함수

        Args:
            file_path (str): 불러올 파일 경로

        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (dict)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return Result(True, None, None, json.load(f))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def load_file(self, file_path):
        """
        파일을 문자열로 불러오는 함수

        Args:
            file_path (str): 불러올 파일 경로

        Returns:
            tuple: (bool, str or None, str or None, str or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (str or dict)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return Result(True, None, None, f.read())
        except Exception as e:
            print(f"Error loading file from {file_path}: {e}")
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_json(self, data, file_path, key=None, serialization=False):
        """
        딕셔너리를 json 파일로 저장하는 함수 (원자적 쓰기 적용)
        - Only JSON files are supported. Other formats Use Atomic_write.

        Args:
            data (dict): 저장할 데이터
            file_path (str): 저장할 파일 경로
            key (str): 저장할 데이터의 키 (선택적)
            serialization (bool): 직렬화 여부
        
        Returns:
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            # 디렉토리가 존재하지 않으면 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
            # 임시 파일 경로 초기화
            temp_file_path = None  

            # 저장할 최종 데이터 준비
            if key is not None:
                # key가 None이 아닌 경우 기존 데이터에 추가
                cache = self.load_json(file_path)
                if os.path.exists(file_path):
                    pass # 파일이 존재하면 기존 데이터를 불러옴
                else:
                    raise FileNotFoundError(f"File '{file_path}' does not exist for updating with key '{key}'.")
                if not cache.success:
                    raise ValueError(f"Failed to load existing JSON file: {file_path}")
                
                existing_data = cache.data
                existing_data[key] = data
                final_data = existing_data
            else:
                # key가 None인 경우 전체 데이터를 덮어쓰기
                final_data = data
            
            # 원자적 쓰기 수행
            self.Atomic_write(json.dumps(final_data, ensure_ascii=False, indent=4) if serialization else json.dumps(final_data), file_path)
            return Result(True, None, None, None)

        except Exception as e:
            print(f"Error saving JSON to {file_path}: {e}")
            # 임시 파일 정리 (이동 실패 시)
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (OSError, Exception) as e:
                    return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
                
    def Atomic_write(self, data, file_path):
        """
        원자적 쓰기를 수행하는 함수

        Args:
            data (str): 저장할 데이터 (문자열)
            file_path (str): 저장할 파일 경로
            ex) Atomic_write("Hello, World!", "./data/example.txt")

        Returns:
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            # 디렉토리가 존재하지 않으면 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 임시 파일 경로 초기화
            temp_file_path = None  
            # 원자적 쓰기: 임시 파일에 먼저 쓰기
            with tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                encoding='utf-8', 
                dir=os.path.dirname(file_path), 
                prefix=os.path.basename(file_path) + '.tmp.'
            ) as tmp:
                tmp.write(data)
                temp_file_path = tmp.name
            
            # 원자적 이동
            shutil.move(temp_file_path, file_path)
            return Result(True, None, None, None)
            
        except Exception as e:
            print(f"Error during atomic write to {file_path}: {e}")
            # 임시 파일 정리 (이동 실패 시)
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (OSError, Exception) as e:
                    return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
                
class ExceptionTracker():
    """
    ExceptionTracker 클래스는 예외 발생 시 위치 정보를 추적하고 관련 정보를 반환하는 기능을 제공합니다.
    
    1. 예외 위치 추적: 예외가 발생한 위치를 추적하고 관련 정보를 반환하는 기능을 제공합니다.
        - get_exception_location: 예외가 발생한 위치를 반환합니다.

    2. 예외 정보 추적: 예외의 정보를 추적하고 관련 정보를 반환하는 기능을 제공합니다.
        - get_exception_info: 예외의 정보를 반환합니다.
    """

    def __init__(self):
        pass

    def get_exception_location(self, error):
        """
        예외가 발생한 위치를 추적하고 관련 정보를 반환하는 함수
        - 정보 형식 (str): '{file}', line {line}, in {function}'
        
        Args:
            error (Exception): 예외 객체 (필수)

        Returns:
            tuple: (bool, str or None, str or None, str or None)
                - 성공 여부 (bool) : True if successful, False otherwise
                - error 메시지 (str or None) : None if successful
                - 컨텍스트 태그 (str or None)  : None if successful
                - 위치 정보 (str) : if failed, traceback string otherwise
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # 가장 최근의 프레임
            return Result(True, None, None, f"'{frame.filename}', line {frame.lineno}, in {frame.name}")
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            return Result(False, f"{type(e).__name__} :{str(e)}", "AppCore.ExceptionTracker.get_exception_location, R315-336", traceback.format_exc())

    def get_exception_info(self, error, user_input=None, params=None):
        """
        예외의 정보를 추적하고 관련 정보를 반환하는 함수
        
        Error 데이터의 dict에는 traceback, 위치 정보, 발생 시각, 입력 컨텍스트 등이 포함되어 있습니다.

        Args:
            error (Exception): 예외 객체 (필수)
            user_input (str): 사용자 입력 (선택적)
            params (dict): 추가 매개변수 (선택적)

        Returns:
            tuple: (bool, str or None, str or None, dict or str)
                - 성공 여부 (bool) : True if successful, False otherwise
                - error 메시지 (str or None) : None if successful
                - 컨텍스트 태그 (str or None)  : None if successful
                - Error 데이터 (dict or str) : dict if successful, traceback string otherwise
                - dict 구조:
                    {
                        "success": bool,
                        "error": {
                            "type": "ExceptionType",
                            "message": "Exception message"
                        },
                        "traceback": "Full traceback string",
                        "location": {
                            "file": "filename",
                            "line": X,
                            "function": "function_name"
                        },
                        "timestamp": "YYYY-MM-DD HH:MM:SS",
                        "context": {
                            "user_input": user_input,
                            "params": params
                        }
                    }
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # 가장 최근의 프레임
            error_info = {
                "success": False,
                "error":{
                    "type": type(error).__name__ if error else "UnknownError", 
                    "message": str(error) if error else "No exception information available"
                },
                "traceback": traceback.format_exc(),
                "location": {
                    "file": frame.filename,
                    "line": frame.lineno,
                    "function": frame.name
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "context": {
                    "user_input": user_input,
                    "params": params
                }
            }
            return Result(True, None, None, error_info)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            return Result(False, f"{type(e).__name__} :{str(e)}", "AppCore.ExceptionTracker.get_exception_location, R338-399", traceback.format_exc())