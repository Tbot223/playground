from typing import NamedTuple, Optional, Any, Union
from dataclasses import dataclass

class Result(NamedTuple):
    """
    Class representing operation results

    NamedTuple version
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any

@dataclass
class ExtendedResult:
    """
    Class representing operation results

    Dataclass version
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any

class ResultUtils:
    """
    Utility class for Result operations
    """
    @staticmethod
    def is_success(result: Union[Result, ExtendedResult]) -> bool:
        """
        Check if the result indicates success
        """
        return result.success

    @staticmethod
    def to_extended(result: Result) -> ExtendedResult:
        """
        Convert NamedTuple Result to ExtendedResult dataclass
        """
        return ExtendedResult(
            success=result.success,
            error=result.error,
            context=result.context,
            data=result.data
        )
    
    @staticmethod
    def to_named_tuple(result: ExtendedResult) -> Result:
        """
        Convert ExtendedResult dataclass to NamedTuple Result
        """
        return Result(
            success=result.success,
            error=result.error,
            context=result.context,
            data=result.data
        )