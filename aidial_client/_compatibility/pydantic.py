import pydantic

PYDANTIC_V2 = pydantic.VERSION.startswith("2.")

__all__ = ["PYDANTIC_V2"]
