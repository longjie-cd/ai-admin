from typing import Optional
from datetime import datetime

_DB: dict[int, dict] = {}
_seq = 1

def list_by_user(user_id: int) -> list[dict]:
    return sorted(
        [t for t in _DB.values() if t["user_id"] == user_id],
        key=lambda x: x["created_at"], reverse=True,
    )

def get_by_id(todo_id: int) -> Optional[dict]:
    return _DB.get(todo_id)

def create(user_id: int, data: dict) -> dict:
    global _seq
    item = {"id": _seq, "user_id": user_id, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **data}
    _DB[_seq] = item
    _seq += 1
    return item

def update(todo_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(todo_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item

def delete(todo_id: int) -> bool:
    return _DB.pop(todo_id, None) is not None
