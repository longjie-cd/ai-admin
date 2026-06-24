from fastapi import APIRouter, Depends
from api.core.deps import get_current_user, get_current_user_obj
from api.core.response import ApiResponse
from api.sys.schedule.schema import ScheduleCreate, ScheduleUpdate
from api.sys.schedule import service

router = APIRouter(prefix="/sys/schedule", tags=["schedule"])

@router.get("", response_model=ApiResponse)
def list_schedules(current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.list_schedules(current_user["id"]).model_dump())

@router.post("", response_model=ApiResponse)
def create_schedule(body: ScheduleCreate, current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.create_schedule(current_user["id"], body).model_dump(), message="创建成功")

@router.put("/{schedule_id}", response_model=ApiResponse)
def update_schedule(schedule_id: int, body: ScheduleUpdate, _=Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_schedule(schedule_id, body).model_dump(), message="更新成功")

@router.delete("/{schedule_id}", response_model=ApiResponse)
def delete_schedule(schedule_id: int, _=Depends(get_current_user)):
    service.delete_schedule(schedule_id)
    return ApiResponse.ok(message="删除成功")
