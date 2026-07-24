from enum import Enum


class SigninResult(str, Enum):
    """Outcome of an interactive sign-in request for a single toolset."""

    SUCCESS = "success"
    DENIED = "denied"
    ERROR = "error"
