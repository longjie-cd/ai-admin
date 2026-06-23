from fastapi import HTTPException, status
from api.sys.menu import crud
from api.sys.menu.schema import MenuCreate, MenuUpdate, MenuOut, MenuListOut
from api.sys.user import crud as user_crud
from api.sys.team import crud as team_crud
from api.sys.role import crud as role_crud


def _build_tree(items: list[dict]) -> list[MenuOut]:
    roots = [_to_out_with_children(item, items) for item in items if item["parent_id"] is None]
    roots.sort(key=lambda x: x.sort)
    return roots


def _to_out_with_children(item: dict, all_items: list[dict]) -> MenuOut:
    children = [
        _to_out_with_children(child, all_items)
        for child in all_items
        if child["parent_id"] == item["id"]
    ]
    children.sort(key=lambda x: x.sort)
    return MenuOut(**item, children=children)


def _get_user_permission_ids(username: str) -> set[int] | None:
    """返回用户的所有权限 IDs（个人 + 部门角色），超级管理员返回 None。"""
    user = user_crud.get_user_by_username(username)
    if not user:
        return set()

    all_role_ids = list(user.get("role_ids", []))

    # 叠加部门角色
    team_id = user.get("team_id")
    if team_id:
        team = team_crud.get_by_id(team_id)
        if team:
            all_role_ids += team.get("role_ids", [])

    permission_ids: set[int] = set()
    for role_id in all_role_ids:
        role = role_crud.get_by_id(role_id)
        if not role:
            continue
        if role.get("code") == "super_admin":
            return None  # 超级管理员不需要过滤
        permission_ids.update(role.get("permission_ids", []))

    return permission_ids


def _filter_menus_by_permissions(menus: list[MenuOut], permission_ids: set[int] | None) -> list[MenuOut]:
    """根据权限过滤菜单树；permission_ids 为 None 时（超级管理员）直接返回。"""
    if permission_ids is None:
        return menus

    filtered = []
    for menu in menus:
        if not menu.permission_ids or any(pid in permission_ids for pid in menu.permission_ids):
            children = _filter_menus_by_permissions(menu.children, permission_ids)
            filtered.append(menu.model_copy(update={"children": children}))

    return filtered


def list_menus() -> MenuListOut:
    items = crud.list_all()
    tree = _build_tree(items)
    return MenuListOut(total=len(items), items=tree)


def list_menus_by_user(username: str) -> MenuListOut:
    """根据用户权限返回动态菜单列表"""
    items = crud.list_all()
    tree = _build_tree(items)

    permission_ids = _get_user_permission_ids(username)
    filtered_tree = _filter_menus_by_permissions(tree, permission_ids)

    return MenuListOut(total=len(items), items=filtered_tree)


def get_menu(menu_id: int) -> MenuOut:
    item = crud.get_by_id(menu_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    all_items = crud.list_all()
    return _to_out_with_children(item, all_items)


def create_menu(body: MenuCreate) -> MenuOut:
    item = crud.create(body.model_dump())
    return MenuOut(**item)


def update_menu(menu_id: int, body: MenuUpdate) -> MenuOut:
    item = crud.update(menu_id, body.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    return MenuOut(**item)


def delete_menu(menu_id: int) -> None:
    if not crud.delete(menu_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
