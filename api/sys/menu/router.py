from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.menu.schema import MenuCreate, MenuUpdate
from api.sys.menu import service

router = APIRouter(prefix="/sys/menu", tags=["menu"])


@router.get("", response_model=ApiResponse)
def list_menus(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_menus().model_dump())


@router.get("/user", response_model=ApiResponse)
def list_menus_by_user(username: str = Depends(get_current_user)):
    """根据当前用户权限返回动态菜单"""
    return ApiResponse.ok(data=service.list_menus_by_user(username).model_dump())


@router.get("/{menu_id}", response_model=ApiResponse)
def get_menu(menu_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_menu(menu_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_menu(body: MenuCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_menu(body).model_dump(), message="创建成功")


@router.put("/{menu_id}", response_model=ApiResponse)
def update_menu(menu_id: int, body: MenuUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_menu(menu_id, body).model_dump(), message="更新成功")


@router.delete("/{menu_id}", response_model=ApiResponse)
def delete_menu(menu_id: int, _: str = Depends(get_current_user)):
    service.delete_menu(menu_id)
    return ApiResponse.ok(message="删除成功")
