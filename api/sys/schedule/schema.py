from pydantic import BaseModel
from typing import Optional

class ScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: str   # ISO date string e.g. "2026-06-24 09:00"
    end_time: str
    all_day: bool = False
    color: str = "#6366F1"

class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    all_day: Optional[bool] = None
    color: Optional[str] = None

class ScheduleOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    start_time: str
    end_time: str
    all_day: bool
    color: str
    created_at: str

class ScheduleListOut(BaseModel):
    total: int
    items: list[ScheduleOut]
