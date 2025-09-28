# external modules
import os
import json
import time
import shutil
from typing import Union, Optional, Tuple, List, Dict
import stat

# internal modules
import AppCore
from Result import Result

class StorageManager:
    """
    StorageManager는 저장 및 불러오기 기능을 담당합니다.

    data 저장, 불러오기, 삭제, 목록화, 유효성 검사 등을 수행합니다.
    모든 데이터는 JSON 형식으로 저장됩니다.
    기본 저장 경로는 ./saves/입니다.
    백업 기능은 추후 구현 예정입니다.

    1. load_data(save_type, save_id="latest")
        - 특정 저장 ID에서 지정된 유형의 데이터를 불러옵니다.

    2. save_data(save_data, save_type, save_id)
        - 특정 저장 ID에 지정된 유형의 데이터를 저장합니다.

    3. save_all(save_id=None)
        - user, stocks 데이터를 모두 저장합니다.
        - save_id가 None이면 새로운 ID를 생성합니다.
        - save_id가 주어지면 해당 ID에 데이터를 덮어씁니다.
        - 새로운 저장을 생성할 때는 save_all을 사용해야 합니다.

    4. save_metadata(save_id)
        - 저장 시간, 유저 이름, 플레이 시간 등 메타데이터 저장

    5. load_metadata(save_id)
        - 저장된 메타데이터 불러오기

    6. list_saves()
        - saves/ 폴더 내의 모든 저장 ID를 반환합니다.
        
    7. delete_save(save_id)
        - 해당 저장 폴더를 삭제합니다.

    8. save_exists(save_id)
        - 특정 저장 ID가 존재하는지 확인합니다.

    9. validate_save(save_id)
        - 필수 파일(user.json, stocks.json 등) 존재 여부 확인
        - 누락된 파일 목록 반환

    10. get_latest_save_id()
        - 가장 최근에 생성된 저장 ID 반환

    11. backup_save(save_id)
        - 현재 필요 없음, 나중에 필요하면 구현
    """
    def __init__(self):
        self.core = AppCore.AppCore()
        self.FileManager = AppCore.FileManager()
        self.exception_tracker = AppCore.ExceptionTracker()
        self.base_dir = "saves"
        self.backup_dir = "backup"
        os.makedirs(self.base_dir, exist_ok=True)

    def load_data(self, save_type, save_id="latest"):
        """
        /saves/(save_id)/(save_type).json 에서 데이터를 불러옵니다.

        Args:
            save_type (str): 불러올 데이터 유형 (stocks, user)
            save_id (str): 불러올 저장 ID (선택적, 기본값 "latest")

        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (dict)
        """
        try:
            if save_id == "latest":
                latest_save = self.get_latest_save_id()
                if latest_save.success is False:
                    raise ValueError("Failed to get latest save ID.")
                save_id = latest_save.data
            file_path = f"saves/{save_id}/{save_type}.json"
            return Result(True, None, None, self.core.FileManager.load_json(file_path))
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_data(self, save_data, save_type, save_id):
        """
        /saves/(save_id)/(save_type).json 에 데이터를 저장합니다.

        Args:
            save_data (dict): 저장할 데이터
            save_type (str): 저장 유형 (stocks, user)
            save_id (str): 저장 ID (필수, 미리 생성한 세이브 파일에만 사용할 것, 세이브 생성은 save_all 사용)

        Returns:
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool), 
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None. Use save_all() to create a new save.")
            file_path = f"saves/{save_id}/{save_type}.json"
            self.FileManager.save_json(save_data, file_path)
            return Result(True, None, None, None)

        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_all(self, data: List[Dict]=None, save_id=None):
        """
        user_data, world_data 등 입력된 데이터를 모두 저장합니다.

        Args:
            save_id (str): 저장 ID (선택적, 기본값 None - 새로운 ID 생성)
            data (list): 저장할 데이터 목록 (필수)
                - 각 항목은 dict 형식이어야 합니다.
                - 예: [{"user_data": user_data}, {"stocks_data": stocks_data}]
                - 다른 형식 사용은 절대 금지!

        Returns: 
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            if data is None:
                raise ValueError("Data must be provided as a list of dictionaries.")
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("All items in data must be of type dict.")
                if not isinstance(next(iter(item.values())), dict):
                    raise ValueError("All items in data must be of type dict.")
                if len(item) != 1:
                    raise ValueError("Each dictionary in data must contain exactly one key-value pair.")
            
            def save_item(item, save_id=None): # 내부 함수로 데이터 저장
                if save_id is not None:
                    for key, value in item.items():
                        file_path = f"saves/{save_id}/{key}.json"
                        self.FileManager.save_json(value, file_path)
                else: # save_id가 None이면 새로운 저장 생성 불가
                    raise ValueError("save_id cannot be None when saving individual items.(inner function, save_item)")

            if save_id is not None: # 저장 ID 주어진 경우
                if not os.path.exists(os.path.join(self.base_dir, save_id)):
                    os.makedirs(os.path.join(self.base_dir, save_id), exist_ok=True)
                self.save_metadata(save_id)
                for item in data: # 주어진 ID에 데이터 덮어쓰기
                    save_item(item, save_id)
                return Result(True, None, None, None)
            else: # 저장 ID 주어지지 않은 경우, 새로운 ID 생성
                i = 1
                while True: # save_1, save_2, ... 순으로 폴더 생성
                    candidate = f"save_{i}" 
                    candidate_path = os.path.join(self.base_dir, candidate) # saves/save_i
                    if not os.path.exists(candidate_path): # 해당 폴더가 없으면 생성
                        os.makedirs(candidate_path, exist_ok=True)
                        self.save_metadata(candidate)
                        for item in data:
                            save_item(item, candidate)
                        return Result(True, None, None, None)
                    i += 1
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_metadata(self, save_id: str, user_name: str, play_time: int):
        """
        저장 시간, 유저 이름, 플레이 시간 등 메타데이터 저장

        Args:
            save_id (str): 저장 ID (필수)
            user_name (str): 유저 이름 (필수)
            play_time (int): 플레이 시간 (초 단위, 필수)

        Returns:
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None.")
            if user_name is None:
                raise ValueError("user_name cannot be None.")
            if play_time is None or not isinstance(play_time, int) or play_time < 0:
                raise ValueError("play_time must be a non-negative integer representing seconds.")
            metadata = {
                "timestamp": time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime()),
                "user_name": user_name,
                "play_time": play_time
            }
            file_path = f"saves/{save_id}/metadata.json"
            self.FileManager.save_json(metadata, file_path)
            return Result(True, None, None, None)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def load_metadata(self, save_id):
        """
        저장된 메타데이터 불러오기

        Args:
            save_id (str): 불러올 저장 ID (필수)

        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (dict)
        """
        try:
            if save_id is None:
                raise ValueError("save_id cannot be None.")
            if not os.path.exists(os.path.join(self.base_dir, save_id)):
                raise FileNotFoundError(f"Save ID '{save_id}' does not exist.")
            file_path = f"saves/{save_id}/metadata.json"
            metadata = self.FileManager.load_json(file_path)
            if not metadata.success:
                raise ValueError("Failed to load metadata.")
            if metadata.data is None:
                raise ValueError("Metadata is None.")
            return Result(True, None, None, metadata.data)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def list_saves(self):
        """
        saves/ 폴더 내의 모든 저장 ID를 반환

        Returns:
            tuple: (bool, str or None, str or None, list or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (list or dict)
        """
        try:
            saves = os.listdir(self.base_dir)
            return Result(True, None, None, saves)
        except Exception as e:
            return Result(False, str(e), self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
    def delete_save(self, save_id):
        """
        해당 저장 폴더를 삭제

        Args:
            save_id (str): 삭제할 저장 ID (필수)

        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            save_path = os.path.join(self.base_dir, save_id) # saves/save_id
            if os.path.exists(save_path):
                try:
                    shutil.rmtree(save_path) # 폴더 및 내부 파일 모두 삭제
                except PermissionError:
                    shutil.rmtree(save_path, onerror=lambda func, p, exc: (os.chmod(p, stat.S_IWRITE), func(p))) # 권한 문제로 삭제 실패 시 권한 변경 후 재시도
                return Result(True, None, None, None)
            else:
                raise FileNotFoundError(f"Save ID '{save_id}' is maybe already deleted or does not exist.")
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_exists(self, save_id):
        """
        특정 저장 ID가 존재하는지 확인

        Args:
            save_id (str): 확인할 저장 ID (필수)

        Returns:
            tuple: (bool, str or None, str or None, bool or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 존재 여부/에러 데이터 (bool or dict)
        """
        try:
            save_path = os.path.join(self.base_dir, save_id)
            return Result(True, None, None, os.path.exists(save_path))
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def validate_save(self, save_id: str, required_files: List = None):
        """
        필수 파일(user.json, metadata.json 등) 존재 여부 확인

        Args:
            save_id (str): 확인할 저장 ID (필수)
            required_files (list, optional): 필수 파일 목록 (필수)
        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 존재 여부/에러 데이터 (dict)
        """
        try:
            if required_files is None:
                raise ValueError("required_files must be provided as a list of filenames.")
            save_path = os.path.join(self.base_dir, save_id)
            searched_file = os.listdir(save_path)
            missing_files = []
            for req_file in required_files:
                if req_file not in searched_file:
                    missing_files.append(req_file)
                else:
                    continue
            if missing_files != []:

                return Result(True, None, None, {"valid": False, "missing_files": missing_files})

            return Result(True, None, None, {"valid": True, "missing_files": None})
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def get_latest_save_id(self):
        """
        가장 최근에 생성된 저장 ID 반환

        Returns:
            tuple: (bool, str or None, str or None, str or dict)
            - 성공 여부 (bool)
            - error 메시지 (str or None)
            - 컨텍스트 태그 (str or None)
            - 최종/에러 데이터 (str or dict)
        """
        try:
            saves = self.list_saves()
            if not saves.success:
                raise ValueError("Failed to list saves.")
            latest_save = None
            latest_time = 0
            for save in saves.data:
                metadata = self.load_metadata(save)
                if isinstance(metadata, tuple) and metadata.success is False:
                    raise ValueError(f"Failed to load metadata for save: {save}")
                timestamp_str = metadata.data.get("timestamp", "")

                timestamp = time.mktime(time.strptime(timestamp_str, "%Y-%m-%d,%H:%M:%S"))
                if timestamp > latest_time:
                    latest_time = timestamp
                    latest_save = save
            if latest_save is None:
                raise ValueError("No valid saves found.")
            return Result(True, None, None, latest_save)
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

# 테스트 코드

"""

user_data = {"name": "Alice", "level": 5, "experience": 1500}
stocks_data = {"AAPL": 10, "GOOGL": 5, "TSLA": 2}
data = [    
        {"user_data": user_data}, 
        {"stocks_data": stocks_data}
       ]    
a = StorageManager().save_all(data)
print(a)
""" 

# b = StorageManager().save_data({"name": "Alice", "level": 5, "experience": 150}, "user_data", "save_1")
# print(b)
    
# print(StorageManager().validate_save("save_1", ["user_data.json", "stocks_data.json", "metadata.json"]))

# print(StorageManager().get_latest_save_id())

# b = StorageManager().delete_save("save_1")
# print(b)

# print(StorageManager().list_saves())

# print(StorageManager().load_data("user_data"))

# print(StorageManager().load_metadata("save_2"))

# print(StorageManager().save_exists("save_2"))

        
        

"""
[StorageManager 업데이트 해야할 기능 목록]

    1. backup_save(save_id) - 현재 필요 없음, 나중에 필요하면 구현
    - 저장 시 backup/ 폴더에 복사본 생성
    - 데이터 손상 대비, 복구 기능과 연계 가능
    
"""