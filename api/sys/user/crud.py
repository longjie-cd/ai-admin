from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_user_by_id(user_id: int) -> Optional[dict]:
    return _DB.get(user_id)


def get_user_by_username(username: str) -> Optional[dict]:
    return next((u for u in _DB.values() if u["username"] == username), None)


def list_users() -> list[dict]:
    return list(_DB.values())


def create_user(data: dict) -> dict:
    global _seq
    user = {"id": _seq, **data}
    _DB[_seq] = user
    _seq += 1
    return user


def update_user(user_id: int, data: dict) -> Optional[dict]:
    user = _DB.get(user_id)
    if not user:
        return None
    for k, v in data.items():
        if v is not None:
            user[k] = v
    return user


def delete_user(user_id: int) -> bool:
    return _DB.pop(user_id, None) is not None
