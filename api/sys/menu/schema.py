from pydantic import BaseModel, Field
from typing import Optional


class MenuCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    path: str = Field(..., min_length=1, max_length=255)
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort: int = 0
    api_id: Optional[int] = None
    permission_ids: list[int] = []


class MenuUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    path: Optional[str] = Field(None, min_length=1, max_length=255)
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort: Optional[int] = None
    api_id: Optional[int] = None
    permission_ids: Optional[list[int]] = None


class MenuOut(BaseModel):
    id: int
    name: str
    path: str
    icon: Optional[str]
    parent_id: Optional[int]
    sort: int
    api_id: Optional[int]
    permission_ids: list[int] = []
    children: list["MenuOut"] = []


MenuOut.model_rebuild()


class MenuListOut(BaseModel):
    total: int
    items: list[MenuOut]
