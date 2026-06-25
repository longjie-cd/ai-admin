from fastapi import APIRouter, Depends
from api.core.deps import get_current_user, get_current_user_obj
from api.core.response import ApiResponse
from api.sys.announcement.schema import AnnouncementCreate, AnnouncementUpdate
from api.sys.announcement import service

router = APIRouter(prefix="/sys/announcement", tags=["announcement"])


@router.get("", response_model=ApiResponse)
def list_announcements(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_announcements().model_dump())


@router.get("/mine", response_model=ApiResponse)
def list_my_announcements(current_user: dict = Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.list_announcements_for_user(current_user).model_dump())


@router.get("/{announcement_id}", response_model=ApiResponse)
def get_announcement(announcement_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_announcement(announcement_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_announcement(body: AnnouncementCreate, current_user: dict = Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.create_announcement(body, current_user["id"]).model_dump(), message="创建成功")


@router.put("/{announcement_id}", response_model=ApiResponse)
def update_announcement(announcement_id: int, body: AnnouncementUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_announcement(announcement_id, body).model_dump(), message="更新成功")


@router.delete("/{announcement_id}", response_model=ApiResponse)
def delete_announcement(announcement_id: int, _: str = Depends(get_current_user)):
    service.delete_announcement(announcement_id)
    return ApiResponse.ok(message="删除成功")
