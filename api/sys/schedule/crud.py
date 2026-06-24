from typing import Optional
from datetime import datetime

_DB: dict[int, dict] = {}
_seq = 1

def list_by_user(user_id: int) -> list[dict]:
    return sorted(
        [s for s in _DB.values() if s["user_id"] == user_id],
        key=lambda x: x["start_time"],
    )

def get_by_id(schedule_id: int) -> Optional[dict]:
    return _DB.get(schedule_id)

def create(user_id: int, data: dict) -> dict:
    global _seq
    item = {"id": _seq, "user_id": user_id, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **data}
    _DB[_seq] = item
    _seq += 1
    return item

def update(schedule_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(schedule_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item

def delete(schedule_id: int) -> bool:
    return _DB.pop(schedule_id, None) is not None
