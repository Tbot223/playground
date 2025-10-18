from typing import NamedTuple, Optional, Any
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