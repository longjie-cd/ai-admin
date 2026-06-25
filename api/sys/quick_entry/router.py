from fastapi import APIRouter, Depends
from api.core.deps import get_current_user, get_current_user_obj
from api.core.response import ApiResponse
from api.sys.quick_entry.schema import QuickEntryCreate, QuickEntryUpdate
from api.sys.quick_entry import service

router = APIRouter(prefix="/sys/quick-entry", tags=["quick_entry"])


@router.get("", response_model=ApiResponse)
def list_entries(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_entries().model_dump())


@router.get("/mine", response_model=ApiResponse)
def list_my_entries(current_user: dict = Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.list_entries_for_user(current_user).model_dump())


@router.get("/{entry_id}", response_model=ApiResponse)
def get_entry(entry_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_entry(entry_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_entry(body: QuickEntryCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_entry(body).model_dump(), message="创建成功")


@router.put("/{entry_id}", response_model=ApiResponse)
def update_entry(entry_id: int, body: QuickEntryUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_entry(entry_id, body).model_dump(), message="更新成功")


@router.delete("/{entry_id}", response_model=ApiResponse)
def delete_entry(entry_id: int, _: str = Depends(get_current_user)):
    service.delete_entry(entry_id)
    return ApiResponse.ok(message="删除成功")
