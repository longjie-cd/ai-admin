from pydantic import BaseModel, Field
from typing import Optional


class QuickEntryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    icon: Optional[str] = None
    path: str = Field(..., min_length=1, max_length=256)
    auth_type: str = Field(default="user", pattern=r"^(user|team|role)$")
    auth_ids: list[int] = []
    sort: int = 0


class QuickEntryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    icon: Optional[str] = None
    path: Optional[str] = Field(None, min_length=1, max_length=256)
    auth_type: Optional[str] = Field(None, pattern=r"^(user|team|role)$")
    auth_ids: Optional[list[int]] = None
    sort: Optional[int] = None


class QuickEntryOut(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    path: str
    auth_type: str
    auth_ids: list[int]
    sort: int
    created_at: str


class QuickEntryListOut(BaseModel):
    total: int
    items: list[QuickEntryOut]
