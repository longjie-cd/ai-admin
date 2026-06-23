from fastapi import HTTPException, status
from api.core.security import hash_password, verify_password
from api.sys.user import crud
from api.sys.user.schema import UserCreate, UserUpdate, UserOut, UserListOut, UpdateProfileRequest
from api.sys.team import crud as team_crud


def get_user(user_id: int) -> UserOut:
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserOut(**user)


def get_user_by_username(username: str) -> UserOut:
    user = crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserOut(**user)


def list_users() -> UserListOut:
    users = crud.list_users()
    return UserListOut(total=len(users), items=[UserOut(**u) for u in users])


def create_user(body: UserCreate) -> UserOut:
    if crud.get_user_by_username(body.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = crud.create_user({
        "username": body.username,
        "hashed_password": hash_password(body.password),
        "nickname": body.nickname,
        "email": body.email,
        "disabled": False,
        "role_ids": body.role_ids,
        "team_id": body.team_id,
        "data_scope": body.data_scope,
        "department_ids": body.department_ids,
    })
    return UserOut(**user)


def update_user(user_id: int, body: UserUpdate) -> UserOut:
    user = crud.update_user(user_id, body.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserOut(**user)


def delete_user(user_id: int) -> None:
    if not crud.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")


def update_user_by_username(username: str, body: UpdateProfileRequest) -> UserOut:
    user = crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    updated = crud.update_user(user["id"], body.model_dump(exclude_unset=True))
    return UserOut(**updated)


def change_password(username: str, old_password: str, new_password: str) -> None:
    user = crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if not verify_password(old_password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    crud.update_user(user["id"], {"hashed_password": hash_password(new_password)})


def get_user_roles(user_id: int) -> dict:
    """获取用户的完整角色列表（个人角色 + 部门角色）"""
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 个人角色
    personal_role_ids = user.get("role_ids", [])

    # 部门角色
    department_role_ids = []
    team_id = user.get("team_id")
    if team_id:
        team = team_crud.get_by_id(team_id)
        if team:
            department_role_ids = team.get("role_ids", [])

    # 合并角色
    all_role_ids = list(set(personal_role_ids + department_role_ids))

    return {
        "user_id": user_id,
        "personal_role_ids": personal_role_ids,
        "department_role_ids": department_role_ids,
        "all_role_ids": all_role_ids,
    }
