from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.api_interface.schema import ApiInterfaceCreate, ApiInterfaceUpdate
from api.sys.api_interface import service

router = APIRouter(prefix="/sys/api", tags=["api_interface"])


@router.get("", response_model=ApiResponse)
def list_apis(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_apis().model_dump())


@router.get("/{api_id}", response_model=ApiResponse)
def get_api(api_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_api(api_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_api(body: ApiInterfaceCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_api(body).model_dump(), message="创建成功")


@router.put("/{api_id}", response_model=ApiResponse)
def update_api(api_id: int, body: ApiInterfaceUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_api(api_id, body).model_dump(), message="更新成功")


@router.delete("/{api_id}", response_model=ApiResponse)
def delete_api(api_id: int, _: str = Depends(get_current_user)):
    service.delete_api(api_id)
    return ApiResponse.ok(message="删除成功")
