from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    title: str
    content: str
    type: str = "info"          # info / success / warning / error
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    send_scope: str = "user"    # user / team / all

class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None

class MessageOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    type: str
    is_read: bool
    created_at: str

class MessageListOut(BaseModel):
    total: int
    items: list[MessageOut]
