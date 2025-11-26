# external Modules
import pytest

# internal Modules
from CoreV2 import Exception

@pytest.fixture(scope="module")
def tracker():
    """
    Fixture to create an ExceptionTracker instance for testing.
    """
    return Exception.ExceptionTracker()

@pytest.mark.usefixtures("tracker")
class TestExceptionTracker:
    def zero_division(self) -> None:
        """
        A method that raises a ZeroDivisionError for testing.
        """
        return 1 / 0
    
    def test_get_exception_location(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_location method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_location(error)
        assert result.success is True
        assert "line" in result.data
        assert "in" in result.data

    def test_get_exception_info(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_info method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_info(error)
        assert result.success is True
        assert result.data["error"]["type"] == "ZeroDivisionError"

        with pytest.raises(ZeroDivisionError) as exc_masking:
            self.zero_division()

        error_masking = exc_masking.value
        result_masking = tracker.get_exception_info(error_masking, masking=True)
        assert result_masking.success is True
        assert result_masking.data["computer_info"] == "<Masked>"

    def test_get_exception_return(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_return method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_return(error)
        assert result.success is False
        assert result.data["error"]["type"] == "ZeroDivisionError"

        with pytest.raises(ZeroDivisionError) as exc_masking:
            self.zero_division()

        error_masking = exc_masking.value
        result_masking = tracker.get_exception_return(error_masking, masking=True)
        assert result_masking.success is False
        assert result_masking.data == "<Masked>"

    def test_system_info_initialization(self) -> None:
        """
        Test that the system info is initialized correctly in ExceptionTracker.
        """
        tracker = Exception.ExceptionTracker()
        assert isinstance(tracker._system_info, dict)
        assert "OS" in tracker._system_info
        assert "Python_Version" in tracker._system_info

    @Exception.ExceptionTrackerDecorator(masking=False, tracker=Exception.ExceptionTracker())
    def dummy_method(self, x: int) -> str:
        """
        A dummy method to test the ExceptionTrackerDecorator.
        """
        return 10 / x

    def test_exception_tracker_decorator(self) -> None:
        """
        Test the ExceptionTrackerDecorator.
        """
        result = self.dummy_method(0)
        
        result.data["error"]["type"] == "ZeroDivisionError"

if __name__ == "__main__":
    pytest.main([__file__])