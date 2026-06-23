from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.permission.schema import PermissionCreate, PermissionUpdate
from api.sys.permission import service

router = APIRouter(prefix="/sys/permission", tags=["permission"])


@router.get("", response_model=ApiResponse)
def list_permissions(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_permissions().model_dump())


@router.get("/{perm_id}", response_model=ApiResponse)
def get_permission(perm_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_permission(perm_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_permission(body: PermissionCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_permission(body).model_dump(), message="创建成功")


@router.put("/{perm_id}", response_model=ApiResponse)
def update_permission(perm_id: int, body: PermissionUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_permission(perm_id, body).model_dump(), message="更新成功")


@router.delete("/{perm_id}", response_model=ApiResponse)
def delete_permission(perm_id: int, _: str = Depends(get_current_user)):
    service.delete_permission(perm_id)
    return ApiResponse.ok(message="删除成功")
