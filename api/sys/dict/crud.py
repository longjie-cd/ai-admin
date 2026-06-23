from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(dict_id: int) -> Optional[dict]:
    return _DB.get(dict_id)


def get_by_code(code: str, parent_id: Optional[int] = None) -> Optional[dict]:
    return next(
        (d for d in _DB.values() if d["code"] == code and d["parent_id"] == parent_id),
        None,
    )


def list_all() -> list[dict]:
    return list(_DB.values())


def list_by_parent(parent_id: Optional[int] = None) -> list[dict]:
    return [d for d in _DB.values() if d["parent_id"] == parent_id]


def create(data: dict) -> dict:
    global _seq
    item = {"id": _seq, **data}
    _DB[_seq] = item
    _seq += 1
    return item


def update(dict_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(dict_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item


def delete(dict_id: int) -> bool:
    return _DB.pop(dict_id, None) is not None
