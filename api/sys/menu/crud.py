from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(menu_id: int) -> Optional[dict]:
    return _DB.get(menu_id)


def list_all() -> list[dict]:
    return list(_DB.values())


def list_by_parent(parent_id: Optional[int] = None) -> list[dict]:
    return [m for m in _DB.values() if m["parent_id"] == parent_id]


def create(data: dict) -> dict:
    global _seq
    item = {"id": _seq, **data}
    _DB[_seq] = item
    _seq += 1
    return item


def update(menu_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(menu_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item


def delete(menu_id: int) -> bool:
    return _DB.pop(menu_id, None) is not None
