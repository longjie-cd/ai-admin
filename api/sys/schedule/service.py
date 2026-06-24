from fastapi import HTTPException
from api.sys.schedule import crud
from api.sys.schedule.schema import ScheduleCreate, ScheduleUpdate, ScheduleOut, ScheduleListOut

def list_schedules(user_id: int) -> ScheduleListOut:
    items = [ScheduleOut(**s) for s in crud.list_by_user(user_id)]
    return ScheduleListOut(total=len(items), items=items)

def create_schedule(user_id: int, body: ScheduleCreate) -> ScheduleOut:
    return ScheduleOut(**crud.create(user_id, body.model_dump()))

def update_schedule(schedule_id: int, body: ScheduleUpdate) -> ScheduleOut:
    s = crud.update(schedule_id, body.model_dump(exclude_unset=True))
    if not s:
        raise HTTPException(status_code=404, detail="日程不存在")
    return ScheduleOut(**s)

def delete_schedule(schedule_id: int) -> None:
    if not crud.delete(schedule_id):
        raise HTTPException(status_code=404, detail="日程不存在")
