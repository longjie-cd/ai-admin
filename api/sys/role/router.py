from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.role.schema import RoleCreate, RoleUpdate
from api.sys.role import service

router = APIRouter(prefix="/sys/role", tags=["role"])


@router.get("", response_model=ApiResponse)
def list_roles(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_roles().model_dump())


@router.get("/{role_id}", response_model=ApiResponse)
def get_role(role_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_role(role_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_role(body: RoleCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_role(body).model_dump(), message="创建成功")


@router.put("/{role_id}", response_model=ApiResponse)
def update_role(role_id: int, body: RoleUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_role(role_id, body).model_dump(), message="更新成功")


@router.delete("/{role_id}", response_model=ApiResponse)
def delete_role(role_id: int, _: str = Depends(get_current_user)):
    service.delete_role(role_id)
    return ApiResponse.ok(message="删除成功")
