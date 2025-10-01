from typing import NamedTuple, Optional, Any

class Result(NamedTuple):
    """
    Class representing operation results
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any