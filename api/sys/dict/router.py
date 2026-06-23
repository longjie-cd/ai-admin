from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.dict.schema import DictCreate, DictUpdate
from api.sys.dict import service

router = APIRouter(prefix="/sys/dict", tags=["dict"])


@router.get("", response_model=ApiResponse)
def list_dicts(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_dicts().model_dump())


@router.get("/flat", response_model=ApiResponse)
def list_dicts_flat(_: str = Depends(get_current_user)):
    items = service.list_dicts_flat()
    return ApiResponse.ok(data=[item.model_dump() for item in items])


@router.get("/{dict_id}", response_model=ApiResponse)
def get_dict(dict_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_dict(dict_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_dict(body: DictCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_dict(body).model_dump(), message="创建成功")


@router.put("/{dict_id}", response_model=ApiResponse)
def update_dict(dict_id: int, body: DictUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_dict(dict_id, body).model_dump(), message="更新成功")


@router.delete("/{dict_id}", response_model=ApiResponse)
def delete_dict(dict_id: int, _: str = Depends(get_current_user)):
    service.delete_dict(dict_id)
    return ApiResponse.ok(message="删除成功")
