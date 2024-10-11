"""
Since we need some protected imports from openai, wrap it with this module,
for easier handling of cases, when such member will migrate to another modules
"""

from openai._models import BaseModel
from openai._types import Omit

__all__ = ["Omit", "BaseModel"]
