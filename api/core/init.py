"""
应用初始化：创建默认团队、超级管理员角色、admin 用户。
幂等设计，已存在则跳过，不会重复创建。
"""
from api.core.security import hash_password
from api.sys.permission import crud as perm_crud
from api.sys.role import crud as role_crud
from api.sys.team import crud as team_crud
from api.sys.user import crud as user_crud

DEFAULT_PASSWORD = "Admin!123"


def run() -> None:
    _init_role()
    _init_team()
    _init_admin()


def _init_role() -> None:
    if role_crud.get_by_code("super_admin"):
        return
    all_perm_ids = [p["id"] for p in perm_crud.list_all()]
    role_crud.create({
        "name": "超级管理员",
        "code": "super_admin",
        "description": "拥有全部权限",
        "permission_ids": all_perm_ids,
    })
    print(f"[init] 角色「超级管理员」已创建，权限数：{len(all_perm_ids)}")


def _init_team() -> None:
    if team_crud.get_by_code("default"):
        return
    team_crud.create({"name": "默认团队", "code": "default", "description": "系统默认团队"})
    print("[init] 团队「默认团队」已创建")


def _init_admin() -> None:
    if user_crud.get_user_by_username("admin"):
        return
    role = role_crud.get_by_code("super_admin")
    team = team_crud.get_by_code("default")
    user_crud.create_user({
        "username": "admin",
        "hashed_password": hash_password(DEFAULT_PASSWORD),
        "nickname": "超级管理员",
        "email": "admin@example.com",
        "disabled": False,
        "role_ids": [role["id"]] if role else [],
        "team_id": team["id"] if team else None,
        "data_scope": "all",
        "department_ids": [],
    })
    print(f"[init] 用户「admin」已创建，默认密码：{DEFAULT_PASSWORD}")


if __name__ == "__main__":
    run()
