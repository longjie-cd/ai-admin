from pydantic import BaseModel, Field
from typing import Optional


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    content: str = Field(..., min_length=1)
    target_type: str = Field(default="user", pattern=r"^(user|team|role)$")
    target_ids: list[int] = []
    push_message: bool = False


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    content: Optional[str] = Field(None, min_length=1)
    target_type: Optional[str] = Field(None, pattern=r"^(user|team|role)$")
    target_ids: Optional[list[int]] = None
    push_message: Optional[bool] = None


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    target_type: str
    target_ids: list[int]
    push_message: bool
    created_at: str
    updated_at: str


class AnnouncementListOut(BaseModel):
    total: int
    items: list[AnnouncementOut]
