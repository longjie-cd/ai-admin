from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(api_id: int) -> Optional[dict]:
    return _DB.get(api_id)


def get_by_path_and_method(path: str, method: str) -> Optional[dict]:
    return next(
        (a for a in _DB.values() if a["path"] == path and a["method"] == method),
        None,
    )


def list_all() -> list[dict]:
    return list(_DB.values())


def create(data: dict) -> dict:
    global _seq
    item = {"id": _seq, **data}
    _DB[_seq] = item
    _seq += 1
    return item


def update(api_id: int, data: dict) -> Optional[dict]:
    item = _DB.get(api_id)
    if not item:
        return None
    for k, v in data.items():
        if v is not None:
            item[k] = v
    return item


def delete(api_id: int) -> bool:
    return _DB.pop(api_id, None) is not None
