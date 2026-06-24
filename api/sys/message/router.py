from fastapi import APIRouter, Depends
from api.core.deps import get_current_user, get_current_user_obj
from api.core.response import ApiResponse
from api.sys.message.schema import MessageCreate, MessageUpdate
from api.sys.message import service

router = APIRouter(prefix="/sys/message", tags=["message"])

@router.get("", response_model=ApiResponse)
def list_messages(current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.list_messages(current_user["id"]).model_dump())

@router.get("/unread-count", response_model=ApiResponse)
def get_unread_count(current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data={"count": service.unread_count(current_user["id"])})

@router.get("/{msg_id}", response_model=ApiResponse)
def get_message(msg_id: int, _=Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_message(msg_id).model_dump())

@router.post("", response_model=ApiResponse)
def create_message(body: MessageCreate, _=Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_message(body).model_dump(), message="创建成功")

@router.put("/mark-all-read", response_model=ApiResponse)
def mark_all_read(current_user=Depends(get_current_user_obj)):
    count = service.mark_all_read(current_user["id"])
    return ApiResponse.ok(data={"count": count}, message=f"已标记 {count} 条为已读")

@router.put("/{msg_id}", response_model=ApiResponse)
def update_message(msg_id: int, body: MessageUpdate, _=Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_message(msg_id, body).model_dump(), message="更新成功")

@router.delete("/{msg_id}", response_model=ApiResponse)
def delete_message(msg_id: int, _=Depends(get_current_user)):
    service.delete_message(msg_id)
    return ApiResponse.ok(message="删除成功")
