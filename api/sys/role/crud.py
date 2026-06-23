from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(role_id: int) -> Optional[dict]:
    return _DB.get(role_id)


def get_by_code(code: str) -> Optional[dict]:
    return next((r for r in _DB.values() if r["code"] == code), None)


def list_all() -> list[dict]:
    return list(_DB.values())


def create(data: dict) -> dict:
    global _seq
    role = {"id": _seq, **data}
    _DB[_seq] = role
    _seq += 1
    return role


def update(role_id: int, data: dict) -> Optional[dict]:
    role = _DB.get(role_id)
    if not role:
        return None
    for k, v in data.items():
        if v is not None:
            role[k] = v
    return role


def delete(role_id: int) -> bool:
    return _DB.pop(role_id, None) is not None
