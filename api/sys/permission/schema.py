from pydantic import BaseModel, Field
from typing import Optional


class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=128, pattern=r"^[\w:]+$")
    group: str = Field(..., min_length=1, max_length=32)
    description: Optional[str] = None


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    group: Optional[str] = Field(None, min_length=1, max_length=32)
    description: Optional[str] = None


class PermissionOut(BaseModel):
    id: int
    name: str
    code: str
    group: str
    description: Optional[str]


class PermissionListOut(BaseModel):
    total: int
    items: list[PermissionOut]
