from typing import Any
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "ok") -> "ApiResponse":
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, message: str, code: int = 1) -> "ApiResponse":
        return cls(code=code, message=message, data=None)
