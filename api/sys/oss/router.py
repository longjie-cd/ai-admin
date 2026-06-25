from fastapi import APIRouter, Body, Depends, Query
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.oss.schema import FileCreate, FileUpdate, UploadTokenRequest
from api.sys.oss import service

router = APIRouter(prefix="/sys/oss", tags=["oss"])


@router.get("", response_model=ApiResponse)
def list_files(
    parent_id: int | None = Query(default=None, description="父级 ID，不传则返回完整树"),
    _: str = Depends(get_current_user),
):
    """获取文件树或指定父级下的文件列表"""
    if parent_id is not None:
        items = service.list_by_parent(parent_id)
        return ApiResponse.ok(data=[item.model_dump() for item in items])
    return ApiResponse.ok(data=service.list_files().model_dump())


@router.get("/{file_id}", response_model=ApiResponse)
def get_file(file_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_file(file_id).model_dump())


@router.post("/upload-token", response_model=ApiResponse)
def get_upload_token(body: UploadTokenRequest, _: str = Depends(get_current_user)):
    """获取 OSS 预签名上传 URL，前端直传文件到 OSS"""
    return ApiResponse.ok(data=service.generate_upload_token(body).model_dump())


@router.post("", response_model=ApiResponse)
def create_file(body: FileCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_file(body).model_dump(), message="创建成功")


@router.put("/{file_id}", response_model=ApiResponse)
def update_file(file_id: int, body: FileUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_file(file_id, body).model_dump(), message="更新成功")


@router.post("/{file_id}/copy", response_model=ApiResponse)
def copy_file(
    file_id: int,
    target_parent_id: int | None = Body(default=None, embed=True),
    _: str = Depends(get_current_user),
):
    """复制文件/文件夹到目标文件夹（target_parent_id=null 表示根目录）"""
    return ApiResponse.ok(data=service.copy_file(file_id, target_parent_id).model_dump(), message="复制成功")


@router.delete("/{file_id}", response_model=ApiResponse)
def delete_file(file_id: int, _: str = Depends(get_current_user)):
    service.delete_file(file_id)
    return ApiResponse.ok(message="删除成功")
