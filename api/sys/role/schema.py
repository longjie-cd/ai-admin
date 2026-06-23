from pydantic import BaseModel, Field
from typing import Optional
from api.sys.permission.schema import PermissionOut


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=64, pattern=r"^\w+$")
    description: Optional[str] = None
    permission_ids: list[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = None
    permission_ids: Optional[list[int]] = None


class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    permission_ids: list[int]
    permissions: list[PermissionOut] = []


class RoleListOut(BaseModel):
    total: int
    items: list[RoleOut]
