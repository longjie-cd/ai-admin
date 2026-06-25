from pydantic import BaseModel, Field
from typing import Optional


class FileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(default="folder", pattern=r"^(folder|file)$")
    parent_id: Optional[int] = None
    size: int = 0
    content_type: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class FileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_id: Optional[int] = None
    description: Optional[str] = None


class FileOut(BaseModel):
    id: int
    name: str
    type: str
    path: str
    parent_id: Optional[int]
    size: int
    content_type: Optional[str]
    url: Optional[str]
    description: Optional[str]
    created_at: str
    updated_at: str
    children: list["FileOut"] = []


FileOut.model_rebuild()


class FileListOut(BaseModel):
    total: int
    items: list[FileOut]


class UploadTokenRequest(BaseModel):
    """前端请求预签名上传 URL"""
    file_name: str = Field(..., min_length=1, max_length=255, description="文件名（含扩展名）")
    content_type: str = Field(default="application/octet-stream", description="文件 MIME 类型")
    parent_id: Optional[int] = Field(default=None, description="目标文件夹 ID，None 表示根目录")
    expire_seconds: int = Field(default=3600, ge=60, le=86400, description="签名有效期（秒）")


class UploadTokenOut(BaseModel):
    """预签名上传凭证"""
    upload_url: str = Field(..., description="预签名 PUT 上传地址")
    file_url: str = Field(..., description="上传完成后文件的访问地址")
    key: str = Field(..., description="OSS 中的对象 key")
    expire: int = Field(..., description="签名过期时间戳（秒）")
