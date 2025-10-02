# external modules
import pytest
import os
from pathlib import Path
import sys

# internal modules
from Core import StorageManager

@pytest.fixture(scope="module")
def setup_module(tmp_path_factory):
    tmp_root = tmp_path_factory.mktemp("StorageManager_root")
    storage_manager = StorageManager.StorageManager(parent_dir=tmp_root)
    return storage_manager

@pytest.mark.usefixtures("tmp_path", "setup_module")
class TestStorageManager:
    def test_save_all_func(self, setup_module):
        storage_manager = setup_module
        tmp_dir = Path(storage_manager.parent_dir)
        test_data = [{"user_data": {"user_data": "test"}}, {"world_data": {"world_data": "test"}}]
        metadata = {"user_name": "tester", "playtime": 100}

        # Test saving data
        save_result = storage_manager.save_all(data=test_data, metadata=metadata, save_id=None)
        print(f"Save result: {save_result}")
        assert save_result.success, f"Save failed: {save_result.error}"

        # Test loading data
        user_data_result = storage_manager.load_data("user_data")
        world_data_result = storage_manager.load_data("world_data")
        print(f"User data result: {user_data_result}")
        print(f"World data result: {world_data_result}")
        
        assert user_data_result.success, f"Load user data failed: {user_data_result.error}"
        assert world_data_result.success, f"Load world data failed: {world_data_result.error}"
        assert user_data_result.data == {"user_data": "test"}
        assert world_data_result.data == {"world_data": "test"}

        # Test overwriting data and last save retrieval
        last_save = storage_manager.get_latest_save_id()
        assert last_save.success, f"Get last save failed: {last_save.error}"

        test_data_overwrite = {"user_data": "test2"}
        save_result_overwrite = storage_manager.save_data(test_data_overwrite, "user_data", last_save.data)
        assert save_result_overwrite.success, f"Overwrite save failed: {save_result_overwrite.error}"
        assert storage_manager.load_data("user_data").data == {"user_data": "test2"}
        
        # metadata
        metadata_result = storage_manager.load_metadata(last_save.data)
        assert metadata_result.success, f"Load metadata failed: {metadata_result.error}"
        assert metadata_result.data["playtime"] == metadata["playtime"], "Metadata does not match"
        assert metadata_result.data["user_name"] == metadata["user_name"], "Metadata does not match"

        # metadata overwrite
        new_metadata = {"user_name": "tester2", "playtime": 200}
        metadata_overwrite_result = storage_manager.save_metadata(last_save.data, new_metadata)
        assert metadata_overwrite_result.success, f"Metadata overwrite failed: {metadata_overwrite_result.error}"
        metadata_result_after = storage_manager.load_metadata(last_save.data)
        assert metadata_result_after.success, f"Load metadata after overwrite failed: {metadata_result_after.error}"
        assert metadata_result_after.data["playtime"] == new_metadata["playtime"], "Metadata after overwrite does not match"
        assert metadata_result_after.data["user_name"] == new_metadata["user_name"], "Metadata after overwrite does not match"

        # list saves
        list_result = storage_manager.list_saves()
        assert list_result.success, f"List saves failed: {list_result.error}"

        # save_exists
        exists_result = storage_manager.save_exists(last_save.data)
        assert exists_result.success, f"Save exists check failed: {exists_result.error}"

        # Validate save
        validate_result = storage_manager.validate_save(last_save.data, ["user_data.json", "world_data.json", "metadata.json"])
        assert validate_result.success, f"Validate save failed: {validate_result.error}"
        assert validate_result.data["valid"], "Save validation failed"

        # delete save
        delete_result = storage_manager.delete_save(last_save.data)
        assert delete_result.success, f"Delete save failed: {delete_result.error}"
        assert not storage_manager.save_exists(last_save.data).data, "Save still exists after deletion"
    


if __name__ == "__main__":
    pytest.main()
