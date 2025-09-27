from typing import NamedTuple, Optional, Any

class Result(NamedTuple):
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any