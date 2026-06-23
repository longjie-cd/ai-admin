from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = None
    email: Optional[str] = None
    role_ids: list[int] = []
    team_id: Optional[int] = None
    data_scope: str = Field(default="personal", description="personal|department|all")
    department_ids: list[int] = []


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None
    role_ids: Optional[list[int]] = None
    team_id: Optional[int] = None
    data_scope: Optional[str] = None
    department_ids: Optional[list[int]] = None


class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    email: Optional[str]
    disabled: bool
    role_ids: list[int] = []
    team_id: Optional[int] = None
    data_scope: str
    department_ids: list[int] = []


class UserListOut(BaseModel):
    total: int
    items: list[UserOut]


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
