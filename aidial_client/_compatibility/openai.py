"""
Since we need some protected imports from openai, wrap it with this module,
for easier handling of cases, when such member will migrate to another modules
"""

from openai._compat import PYDANTIC_V2
from openai._models import BaseModel
from openai._types import Omit

__all__ = ["Omit", "PYDANTIC_V2", "BaseModel"]
