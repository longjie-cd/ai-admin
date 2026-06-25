from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(announcement_id: int) -> Optional[dict]:
    return _DB.get(announcement_id)


def list_all() -> list[dict]:
    return sorted(_DB.values(), key=lambda x: x["created_at"], reverse=True)


def create(data: dict) -> dict:
    global _seq
    item = {"id": _seq, **data}
    _DB[_seq] = item
    _seq += 1
    return item


def update(announcement_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(announcement_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item


def delete(announcement_id: int) -> bool:
    return _DB.pop(announcement_id, None) is not None
