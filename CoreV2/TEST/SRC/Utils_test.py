# external Modules
import pytest
from pathlib import Path
import time

# internal Modules
from CoreV2 import Utils

@pytest.fixture(scope="module")
def setup_module():
    """
    Fixture to create Utils, DecoratorUtils, and GlobalVars instances for testing.
    """
    utils = Utils.Utils(is_logging_enabled=True)
    decorator_utils = Utils.DecoratorUtils()
    global_vars = Utils.GlobalVars(is_logging_enabled=True)
    return utils, decorator_utils, global_vars

@pytest.mark.usefixtures("setup_module")
class TestUtils:
    def test_str_to_path(self, setup_module):
        utils, _, _ = setup_module
        path_str = "some/directory/path"
        path_obj = utils.str_to_path(path_str)
        assert path_obj.success, f"Failed to convert string to path: {path_obj.error}"
        assert isinstance(path_obj.data, type(Path())), "Converted data is not a Path object"
        assert str(path_obj.data) == path_str, "Path string does not match the original string"

    def test_encrypt(self, setup_module):
        utils, _, _ = setup_module
        original_text = "Hello, World!"

        for algorithm in ["md5", "sha1", "sha256", "sha512"]:
            encrypted = utils.encrypt(data=original_text, algorithm=algorithm)
            assert encrypted.success, f"Encryption with {algorithm} failed: {encrypted.error}"
            assert encrypted.data != original_text, f"Encrypted text with {algorithm} should not match the original text"

    def test_pbkdf2_hmac(self, setup_module):
        utils, _, _ = setup_module
        password = "securepassword"
        salt_size = 16
        iterations = 100000
        algorithm = "sha256"

        result = utils.pbkdf2_hmac(password=password, algorithm=algorithm, salt_size=salt_size, iterations=iterations)
        assert result.success, f"PBKDF2-HMAC failed: {result.error}"

        verified = utils.verify_pbkdf2_hmac(password=password, salt_hex=result.data['salt_hex'], 
                                            hash_hex=result.data['hash_hex'], algorithm=algorithm, iterations=iterations)
        assert verified.success, f"PBKDF2-HMAC verification failed: {verified.error}"
        assert verified.data is True, "PBKDF2-HMAC verification returned False"

@pytest.mark.usefixtures("setup_module")
class TestDecoratorUtils:
    def test_count_runtime(self, setup_module):
        _, decorator_utils, _ = setup_module

        @decorator_utils.count_runtime()
        def sample_function(delay_time):
            time.sleep(delay_time)
            return "Completed"

        delay = 1  # seconds
        result = sample_function(delay)
        assert result == "Completed", "Sample function did not return expected result"

@pytest.mark.usefixtures("setup_module")
class TestGlobalVars:
    def test_set_and_get_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "test_var"
        value = 42

        # Set global variable
        set_result = global_vars.set(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Get global variable
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get global variable: {get_result.error}"
        assert get_result.data == value, "Retrieved value does not match the set value"

        # Test overwriting the variable
        new_value = 100
        set_result = global_vars.set(key, new_value, overwrite=True)
        assert set_result.success, f"Failed to overwrite global variable: {set_result.error}"
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get overwritten global variable: {get_result.error}"
        assert get_result.data == new_value, "Retrieved value does not match the overwritten value"

    def test_attribute_access(self, setup_module):
        _, _, global_vars = setup_module

        key = "attr_var"
        value = "attribute_value"

        # Set global variable
        global_vars.attr_var = value

        # Access as attribute
        attr_value = global_vars.attr_var
        assert attr_value == value, "Attribute access did not return the expected value"

    def test_call_syntax(self, setup_module):
        _, _, global_vars = setup_module

        key = "call_var"
        value = [1, 2, 3]

        # Set global variable
        set_result = global_vars(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Access using call syntax
        call_value = global_vars(key)
        assert call_value.data == value, "Call syntax did not return the expected value"
    
    def test_delete_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "delete_var"
        value = "to be deleted"

        # Set global variable
        set_result = global_vars.set(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Delete global variable
        delete_result = global_vars.delete(key)
        assert delete_result.success, f"Failed to delete global variable: {delete_result.error}"

        # Try to get deleted variable
        get_result = global_vars.get(key)
        assert not get_result.success, "Deleted variable should not be retrievable"

    def test_clear_global_vars(self, setup_module):
        _, _, global_vars = setup_module

        # Set multiple global variables
        global_vars.set("var1", 1)
        global_vars.set("var2", 2)

        # Clear all global variables
        clear_result = global_vars.clear()
        assert clear_result.success, f"Failed to clear global variables: {clear_result.error}"

        # Verify that variables are cleared
        get_result1 = global_vars.get("var1")
        get_result2 = global_vars.get("var2")
        assert not get_result1.success, "var1 should not be retrievable after clear"
        assert not get_result2.success, "var2 should not be retrievable after clear"

    def test_list_global_vars(self, setup_module):
        _, _, global_vars = setup_module

        # Clear any existing variables
        global_vars.clear()

        # Set multiple global variables
        global_vars.set("list_var1", "value1")
        global_vars.set("list_var2", "value2")

        # List global variables
        list_result = global_vars.list_vars()
        assert list_result.success, f"Failed to list global variables: {list_result.error}"
        assert "list_var1" in list_result.data, "list_var1 not found in global variables list"
        assert "list_var2" in list_result.data, "list_var2 not found in global variables list"
        
    def test_exists_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "exists_var"
        value = "exists"

        # Ensure variable does not exist
        exists_result = global_vars.exists(key)
        assert exists_result.success, f"Exists check failed: {exists_result.error}"
        assert exists_result.data is False, "Variable should not exist yet"

        # Set global variable
        global_vars.set(key, value)

        # Check existence again
        exists_result = global_vars.exists(key)
        assert exists_result.success, f"Exists check failed: {exists_result.error}"
        assert exists_result.data is True, "Variable should exist now"
        
    def test_nonexistent_var_access(self, setup_module):
        _, _, global_vars = setup_module

        key = "nonexistent_var"

        # Try to get a nonexistent variable
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a nonexistent variable should fail"

        # Try to delete a nonexistent variable
        delete_result = global_vars.delete(key)
        assert not delete_result.success, "Deleting a nonexistent variable should fail"

    def test_overwrite_protection(self, setup_module):
        _, _, global_vars = setup_module

        key = "protected_var"
        value = "initial_value"

        # Set global variable
        global_vars.set(key, value)

        # Attempt to overwrite without permission
        set_result = global_vars.set(key, "new_value", overwrite=False)
        assert not set_result.success, "Overwriting without permission should fail"

        # Verify value remains unchanged
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get variable: {get_result.error}"
        assert get_result.data == value, "Variable value should remain unchanged"

class TestEdgeCases:
    def test_empty_key(self, setup_module):
        _, _, global_vars = setup_module

        key = ""
        value = "empty_key_value"

        # Set global variable with empty key
        set_result = global_vars.set(key, value)
        assert not set_result.success, "Setting a variable with an empty key should fail"

        # Get global variable with empty key
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a variable with an empty key should fail"

        # set None as key
        key = None
        set_result = global_vars.set(key, value)
        assert not set_result.success, "Setting a variable with None as key should fail"
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a variable with None as key should fail"

if __name__ == "__main__":
    pytest.main([__file__, "-vv"])