from fastapi import HTTPException, status
from api.sys.role import crud
from api.sys.role.schema import RoleCreate, RoleUpdate, RoleOut, RoleListOut
from api.sys.permission.crud import get_by_id as get_perm
from api.sys.permission.schema import PermissionOut


def _with_permissions(role: dict) -> RoleOut:
    perms = [PermissionOut(**get_perm(pid)) for pid in role["permission_ids"] if get_perm(pid)]
    return RoleOut(**role, permissions=perms)


def list_roles() -> RoleListOut:
    items = [_with_permissions(r) for r in crud.list_all()]
    return RoleListOut(total=len(items), items=items)


def get_role(role_id: int) -> RoleOut:
    role = crud.get_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return _with_permissions(role)


def create_role(body: RoleCreate) -> RoleOut:
    if crud.get_by_code(body.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色码已存在")
    return _with_permissions(crud.create(body.model_dump()))


def update_role(role_id: int, body: RoleUpdate) -> RoleOut:
    role = crud.update(role_id, body.model_dump(exclude_unset=True))
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return _with_permissions(role)


def delete_role(role_id: int) -> None:
    if not crud.delete(role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
