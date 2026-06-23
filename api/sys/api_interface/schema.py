from pydantic import BaseModel, Field
from typing import Optional


class ApiInterfaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    path: str = Field(..., min_length=1, max_length=255)
    method: str = Field(default="GET", max_length=16)
    description: Optional[str] = None
    openapi_url: Optional[str] = None


class ApiInterfaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    path: Optional[str] = Field(None, min_length=1, max_length=255)
    method: Optional[str] = Field(None, max_length=16)
    description: Optional[str] = None
    openapi_url: Optional[str] = None


class ApiInterfaceOut(BaseModel):
    id: int
    name: str
    path: str
    method: str
    description: Optional[str]
    openapi_url: Optional[str]


class ApiInterfaceListOut(BaseModel):
    total: int
    items: list[ApiInterfaceOut]
