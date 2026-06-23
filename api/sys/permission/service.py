from fastapi import HTTPException, status
from api.sys.permission import crud
from api.sys.permission.schema import PermissionCreate, PermissionUpdate, PermissionOut, PermissionListOut


def list_permissions() -> PermissionListOut:
    items = [PermissionOut(**p) for p in crud.list_all()]
    return PermissionListOut(total=len(items), items=items)


def get_permission(perm_id: int) -> PermissionOut:
    p = crud.get_by_id(perm_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    return PermissionOut(**p)


def create_permission(body: PermissionCreate) -> PermissionOut:
    if crud.get_by_code(body.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="权限码已存在")
    return PermissionOut(**crud.create(body.model_dump()))


def update_permission(perm_id: int, body: PermissionUpdate) -> PermissionOut:
    p = crud.update(perm_id, body.model_dump(exclude_unset=True))
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    return PermissionOut(**p)


def delete_permission(perm_id: int) -> None:
    if not crud.delete(perm_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
