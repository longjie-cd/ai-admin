from pydantic import BaseModel, Field
from typing import Optional


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=64, pattern=r"^\w+$")
    description: Optional[str] = None
    role_ids: list[int] = []


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = None
    role_ids: Optional[list[int]] = None


class TeamMemberUpdate(BaseModel):
    user_ids: list[int]


class TeamOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    user_ids: list[int]
    role_ids: list[int] = []
    member_count: int


class TeamListOut(BaseModel):
    total: int
    items: list[TeamOut]
