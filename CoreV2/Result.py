#external Modules
from typing import Any, NamedTuple, Optional

#internal Modules

"""
Do not add any functionality here for now. This file exists to differentiate between Core and CoreV2 modules.

Avoid using ExtendedResult or ResultUtils in CoreV2 for now, as dataclass features or conversion utilities are not currently needed.
"""
class Result(NamedTuple):
    """
    Class representing operation results in CoreV2

    NamedTuple version
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any