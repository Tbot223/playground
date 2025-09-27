# external modules
import os
import json
import time
import shutil

# internal modules
import AppCore
import Result

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
        self.FileManager = AppCore.FileManager
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

    def save_all(self, save_id=None):
        """
        user, stocks 데이터를 모두 저장합니다.

        Args:
            save_id (str): 저장 ID (선택적, 기본값 None - 새로운 ID 생성)

        Returns: 
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            user_data = {"example_key": "example_value"} #ss self.menu.get_user_data()
            stocks_data = {"example_stock": 100} # self.menu.get_stocks_data()

            if save_id is not None:
                file_path_user = f"saves/{save_id}/user.json"
                file_path_stocks = f"saves/{save_id}/stocks.json"
                self.save_metadata(save_id)
                self.FileManager.save_json(user_data, file_path_user)
                self.FileManager.save_json(stocks_data, file_path_stocks)
                return Result(True, None, None, None)
            else:
                i = 1
                while True:
                    candidate = f"save_{i}"
                    candidate_path = os.path.join(self.base_dir, candidate)
                    if not os.path.exists(candidate_path):
                        os.makedirs(candidate_path, exist_ok=True)
                        user_path = f"saves/{candidate}/user.json"
                        stocks_path = f"saves/{candidate}/stocks.json"
                        self.save_metadata(candidate)
                        self.FileManager.save_json(user_data, user_path)
                        self.FileManager.save_json(stocks_data, stocks_path)
                        #still developing
                        return Result(True, None, None, None)
                    i += 1
        except Exception as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)

    def save_metadata(self, save_id):
        """
        저장 시간, 유저 이름, 플레이 시간 등 메타데이터 저장

        Args:
            save_id (str): 저장 ID (필수)

        Returns:
            tuple: (bool, str or None, str or None, None or dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 최종/에러 데이터 (None or dict)
        """
        try:
            metadata = {
                "timestamp": time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime()),
                "user_name": "example_user",  # self.menu.get_user_name()
                "play_time": 3600  # self.menu.get_play_time()
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
            file_path = f"saves/{save_id}/metadata.json"
            return Result(True, None, None, self.FileManager.load_json(file_path))
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
            save_path = os.path.join(self.base_dir, save_id)
            if os.path.exists(save_path):
                shutil.rmtree(save_path)
                return Result(True, None, None, None)
            else:
                raise FileNotFoundError(f"Save ID '{save_id}' does not exist.")
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

    def validate_save(self, save_id):
        """
        필수 파일(user.json, stocks.json 등) 존재 여부 확인

        Args:
            save_id (str): 확인할 저장 ID (필수)

        Returns:
            tuple: (bool, str or None, str or None, dict)
                - 성공 여부 (bool)
                - error 메시지 (str or None)
                - 컨텍스트 태그 (str or None)
                - 존재 여부/에러 데이터 (dict)
        """
        try:
            required_files = ["user.json", "stocks.json", "metadata.json"]
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
            if saves[0] is False:
                raise ValueError("Failed to list saves.")
            latest_save = None
            latest_time = 0
            for save in saves:
                    metadata = self.load_metadata(save)
                    if isinstance(metadata, tuple) and metadata[0] is False:
                        raise ValueError(f"Failed to load metadata for save: {save}")
                    timestamp_str = metadata.get("timestamp", "")
                    try:
                        timestamp = time.mktime(time.strptime(timestamp_str, "%Y-%m-%d,%H:%M:%S"))
                        if timestamp > latest_time:
                            latest_time = timestamp
                            latest_save = save
                    except ValueError:
                        continue
            if latest_save is None:
                raise ValueError("No valid saves found.")
            return Result(True, None, None, latest_save)
        except ValueError as e:
            return Result(False, f"{type(e).__name__} :{str(e)}", self.exception_tracker.get_exception_location(e).data, self.exception_tracker.get_exception_info(e).data)
        
# StorageManager().save_all()
        
# print(StorageManager().validate_save("save_1"))

# print(StorageManager().get_latest_save_id())


        
        

"""
[StorageManager 업데이트 해야할 기능 목록]

    1. backup_save(save_id) - 현재 필요 없음, 나중에 필요하면 구현
    - 저장 시 backup/ 폴더에 복사본 생성
    - 데이터 손상 대비, 복구 기능과 연계 가능
    
"""