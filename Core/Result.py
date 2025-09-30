from typing import NamedTuple, Optional, Any

class Result(NamedTuple):
    """
    작업 결과를 나타내는 클래스
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any