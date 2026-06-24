from fastapi import HTTPException, status
from api.sys.dict import crud
from api.sys.dict.schema import DictCreate, DictUpdate, DictOut, DictListOut


def _build_tree(items: list[dict]) -> list[DictOut]:
    """递归构建树结构，parent_id=None 的为根节点。"""
    roots = [_to_out_with_children(item, items) for item in items if item["parent_id"] is None]
    return roots


def _to_out_with_children(item: dict, all_items: list[dict]) -> DictOut:
    """构建单个节点及其子节点。"""
    children = [
        _to_out_with_children(child, all_items)
        for child in all_items
        if child["parent_id"] == item["id"]
    ]
    return DictOut(**item, children=children)


def list_dicts() -> DictListOut:
    items = crud.list_all()
    tree = _build_tree(items)
    return DictListOut(total=len(items), items=tree)


def list_dicts_flat() -> list[DictOut]:
    """不分组，返回扁平列表。"""
    items = crud.list_all()
    return [DictOut(**item) for item in items]


def get_dict(dict_id: int) -> DictOut:
    item = crud.get_by_id(dict_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典不存在")
    all_items = crud.list_all()
    return _to_out_with_children(item, all_items)


def get_dict_by_code(code: str, parent_id=None):
    item = crud.get_by_code(code, parent_id)
    if not item:
        return None
    return DictOut(**item)


def create_dict(body: DictCreate) -> DictOut:
    if crud.get_by_code(body.code, body.parent_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="字典编码已存在")
    item = crud.create(body.model_dump())
    return DictOut(**item)


def update_dict(dict_id: int, body: DictUpdate) -> DictOut:
    item = crud.update(dict_id, body.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典不存在")
    return DictOut(**item)


def delete_dict(dict_id: int) -> None:
    if not crud.delete(dict_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典不存在")
