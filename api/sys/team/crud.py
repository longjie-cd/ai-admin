from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(team_id: int) -> Optional[dict]:
    return _DB.get(team_id)


def get_by_name(name: str) -> Optional[dict]:
    return next((t for t in _DB.values() if t["name"] == name), None)


def get_by_code(code: str) -> Optional[dict]:
    return next((t for t in _DB.values() if t["code"] == code), None)


def list_all() -> list[dict]:
    return list(_DB.values())


def create(data: dict) -> dict:
    global _seq
    team = {"id": _seq, "user_ids": [], "role_ids": [], **data}
    _DB[_seq] = team
    _seq += 1
    return team


def update(team_id: int, data: dict) -> Optional[dict]:
    team = _DB.get(team_id)
    if not team:
        return None
    team.update({k: v for k, v in data.items() if v is not None})
    return team


def set_members(team_id: int, user_ids: list[int]) -> Optional[dict]:
    team = _DB.get(team_id)
    if not team:
        return None
    team["user_ids"] = user_ids
    return team


def delete(team_id: int) -> bool:
    return _DB.pop(team_id, None) is not None
