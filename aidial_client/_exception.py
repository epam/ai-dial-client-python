from http import HTTPStatus
from typing import Mapping, Optional


class DialException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        type: Optional[str] = "runtime_error",
        param: Optional[str] = None,
        code: Optional[str] = None,
        display_message: Optional[str] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.type = type
        self.param = param
        self.code = code
        self.display_message = display_message

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r},"
            f"status_code={self.status_code!r},"
            f"type={self.type!r},"
            f"param={self.param!r},"
            f"code={self.code!r},"
            f"display_message={self.display_message!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_error_data(
        cls, status_code: int, error_data: Mapping
    ) -> "DialException":
        message = error_data["message"]
        assert isinstance(message, str)
        return cls(
            message=message,
            status_code=status_code,
            type=error_data.get("type"),
            param=error_data.get("param"),
            code=error_data.get("code"),
            display_message=error_data.get("display_message"),
        )


class InvalidRequestError(DialException):
    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(
            message=message,
            type="invalid_request_error",
            status_code=HTTPStatus.BAD_REQUEST,
            **kwargs,
        )


class InvalidDialURLError(InvalidRequestError):
    pass


class NotDialURLError(InvalidRequestError):
    pass


class ParsingDataError(DialException):
    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            **kwargs,
        )


class EtagMismatchError(DialException):
    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.PRECONDITION_FAILED,
            **kwargs,
        )


class ResourceNotFoundError(DialException):
    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            **kwargs,
        )
