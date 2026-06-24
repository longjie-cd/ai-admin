from typing import Optional
from datetime import datetime

_DB: dict[int, dict] = {}
_seq = 1

def list_by_user(user_id: int) -> list[dict]:
    return sorted(
        [m for m in _DB.values() if m["user_id"] == user_id],
        key=lambda x: x["created_at"], reverse=True,
    )

def get_by_id(msg_id: int) -> Optional[dict]:
    return _DB.get(msg_id)

def create(data: dict) -> dict:
    global _seq
    item = {"id": _seq, "is_read": False, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **data}
    _DB[_seq] = item
    _seq += 1
    return item

def update(msg_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(msg_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item

def mark_all_read(user_id: int) -> int:
    count = 0
    for m in _DB.values():
        if m["user_id"] == user_id and not m["is_read"]:
            m["is_read"] = True
            count += 1
    return count

def delete(msg_id: int) -> bool:
    return _DB.pop(msg_id, None) is not None

def unread_count(user_id: int) -> int:
    return sum(1 for m in _DB.values() if m["user_id"] == user_id and not m["is_read"])
