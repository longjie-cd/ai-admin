from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.user.schema import UserCreate, UserUpdate, ChangePasswordRequest, UpdateProfileRequest
from api.sys.user import service

router = APIRouter(prefix="/sys/user", tags=["user"])


@router.get("", response_model=ApiResponse)
def list_users(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_users().model_dump())


@router.get("/{user_id}", response_model=ApiResponse)
def get_user(user_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_user(user_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_user(body: UserCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_user(body).model_dump(), message="创建成功")


@router.put("/{user_id}", response_model=ApiResponse)
def update_user(user_id: int, body: UserUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_user(user_id, body).model_dump(), message="更新成功")


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(user_id: int, _: str = Depends(get_current_user)):
    service.delete_user(user_id)
    return ApiResponse.ok(message="删除成功")


@router.get("/profile/me", response_model=ApiResponse)
def get_profile(username: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_user_by_username(username).model_dump())


@router.put("/profile/me", response_model=ApiResponse)
def update_profile(body: UpdateProfileRequest, username: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_user_by_username(username, body).model_dump(), message="更新成功")


@router.post("/profile/change-password", response_model=ApiResponse)
def change_password(body: ChangePasswordRequest, username: str = Depends(get_current_user)):
    service.change_password(username, body.old_password, body.new_password)
    return ApiResponse.ok(message="密码修改成功")


@router.get("/{user_id}/roles", response_model=ApiResponse)
def get_user_roles(user_id: int, _: str = Depends(get_current_user)):
    """获取用户的完整角色列表（个人角色 + 部门角色）"""
    return ApiResponse.ok(data=service.get_user_roles(user_id))
