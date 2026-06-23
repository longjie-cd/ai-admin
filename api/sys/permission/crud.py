from typing import Optional

_DB: dict[int, dict] = {
    1: {"id": 1, "name": "用户列表", "code": "sys:user:list", "group": "用户管理", "description": ""},
    2: {"id": 2, "name": "创建用户", "code": "sys:user:create", "group": "用户管理", "description": ""},
    3: {"id": 3, "name": "编辑用户", "code": "sys:user:edit", "group": "用户管理", "description": ""},
    4: {"id": 4, "name": "删除用户", "code": "sys:user:delete", "group": "用户管理", "description": ""},
    5: {"id": 5, "name": "团队列表", "code": "sys:team:list", "group": "团队管理", "description": ""},
    6: {"id": 6, "name": "创建团队", "code": "sys:team:create", "group": "团队管理", "description": ""},
    7: {"id": 7, "name": "编辑团队", "code": "sys:team:edit", "group": "团队管理", "description": ""},
    8: {"id": 8, "name": "删除团队", "code": "sys:team:delete", "group": "团队管理", "description": ""},
    9: {"id": 9, "name": "角色列表", "code": "sys:role:list", "group": "角色管理", "description": ""},
    10: {"id": 10, "name": "创建角色", "code": "sys:role:create", "group": "角色管理", "description": ""},
    11: {"id": 11, "name": "编辑角色", "code": "sys:role:edit", "group": "角色管理", "description": ""},
    12: {"id": 12, "name": "删除角色", "code": "sys:role:delete", "group": "角色管理", "description": ""},
}
_seq = 13


def get_by_id(perm_id: int) -> Optional[dict]:
    return _DB.get(perm_id)


def get_by_code(code: str) -> Optional[dict]:
    return next((p for p in _DB.values() if p["code"] == code), None)


def list_all() -> list[dict]:
    return list(_DB.values())


def create(data: dict) -> dict:
    global _seq
    perm = {"id": _seq, **data}
    _DB[_seq] = perm
    _seq += 1
    return perm


def update(perm_id: int, data: dict) -> Optional[dict]:
    perm = _DB.get(perm_id)
    if not perm:
        return None
    perm.update({k: v for k, v in data.items() if v is not None})
    return perm


def delete(perm_id: int) -> bool:
    return _DB.pop(perm_id, None) is not None
