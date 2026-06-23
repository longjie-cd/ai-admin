from pydantic import BaseModel, Field
from typing import Optional


class DictCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=64, pattern=r"^\w+$")
    value: str = Field(..., max_length=255)
    type: str = Field(default="string", max_length=32)
    parent_id: Optional[int] = None
    sort: int = 0
    description: Optional[str] = None


class DictUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    value: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=32)
    parent_id: Optional[int] = None
    sort: Optional[int] = None
    description: Optional[str] = None


class DictOut(BaseModel):
    id: int
    name: str
    code: str
    value: str
    type: str
    parent_id: Optional[int]
    sort: int
    description: Optional[str]
    children: list["DictOut"] = []


DictOut.model_rebuild()


class DictListOut(BaseModel):
    total: int
    items: list[DictOut]
