"""OSS 文件管理 Service 层 —— 将 OSS 扁平结构映射为树形 API。"""
from datetime import datetime

from fastapi import HTTPException, status
from api.sys.oss import crud
from api.sys.oss.schema import FileCreate, FileUpdate, FileOut, FileListOut, UploadTokenRequest, UploadTokenOut


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _build_tree(items: list[dict]) -> list[FileOut]:
    """递归构建树结构，parent_id=None 的为根节点。"""
    roots = [_to_out_with_children(item, items) for item in items if item["parent_id"] is None]
    return roots


def _to_out_with_children(item: dict, all_items: list[dict]) -> FileOut:
    children = [
        _to_out_with_children(child, all_items)
        for child in all_items
        if child["parent_id"] == item["id"]
    ]
    children.sort(key=lambda x: (x.type != "folder", x.name))
    return FileOut(**item, children=children)


def list_files() -> FileListOut:
    """获取完整文件树。"""
    items = crud.list_all()
    tree = _build_tree(items)
    return FileListOut(total=len(items), items=tree)


def list_by_parent(parent_id: int | None = None) -> list[FileOut]:
    """返回指定父级下的直接子项。"""
    items = crud.list_by_parent(parent_id)
    return [FileOut(**item) for item in items]


def get_file(file_id: int) -> FileOut:
    """获取文件/文件夹详情（含子项树）。"""
    item = crud.get_by_id(file_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    all_items = crud.list_all()
    return _to_out_with_children(item, all_items)


def _resolve_parent_key(parent_id: int | None) -> str:
    """将 parent_id 转换为 OSS key 前缀路径。

    返回的路径不以 '/' 开头，不以 '/' 结尾（用于拼接）。
    """
    if parent_id is None:
        return ""
    parent = crud.get_by_id(parent_id)
    if not parent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="父级目录不存在")
    if parent["type"] != "folder":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="父级不是文件夹")
    return parent["path"].lstrip("/")


def create_file(body: FileCreate) -> FileOut:
    """在 OSS 中创建文件夹或文件。"""
    parent_key = _resolve_parent_key(body.parent_id)
    name = body.name.strip("/")

    # 检查同级目录下是否有同名项
    siblings = crud.list_by_parent(body.parent_id)
    if any(s["name"] == name for s in siblings):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="同名文件已存在")

    # 构造完整 key
    key = f"{parent_key}/{name}" if parent_key else name

    if body.type == "folder":
        node = crud.create_folder(key)
    else:
        # 文件：如果有 URL，从 URL 下载后上传到 OSS；否则创建空文件
        import httpx
        content = b""
        content_type = body.content_type
        if body.url:
            try:
                resp = httpx.get(body.url, timeout=30, follow_redirects=True)
                resp.raise_for_status()
                content = resp.content
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无法从 URL 下载文件: {body.url}",
                )
        node = crud.create_file(key, content, content_type)

    return FileOut(**node)


def update_file(file_id: int, body: FileUpdate) -> FileOut:
    """更新文件/文件夹（支持重命名 + 移动）。"""
    item = crud.get_by_id(file_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    data = body.model_dump(exclude_unset=True)
    old_path = item["path"].lstrip("/")
    new_name = data.get("name", item["name"]).strip("/")
    new_parent_id = data.get("parent_id", item["parent_id"])

    # 计算新父级 key
    new_parent_key = _resolve_parent_key(new_parent_id)
    new_path = f"{new_parent_key}/{new_name}" if new_parent_key else new_name

    # 检查同级目录下是否有同名
    siblings = crud.list_by_parent(new_parent_id)
    if any(s["name"] == new_name and s["id"] != file_id for s in siblings):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="同名文件已存在")

    if new_path != old_path:
        # 需要移动
        if crud.object_exists(old_path):
            if item["type"] == "folder":
                # 文件夹移动：复制所有子对象到新路径，再删除旧前缀
                all_items = crud.list_all()
                for node in all_items:
                    node_path = node["path"].lstrip("/")
                    if node_path.startswith(old_path + "/") or node_path == old_path:
                        if node["type"] == "file":
                            rel = node_path[len(old_path):]
                            crud.copy_object(node_path, new_path + rel)
                crud.delete_prefix(old_path)
            else:
                # 文件移动：复制后删除
                crud.copy_object(old_path, new_path)
                crud.delete_object(old_path)

    # 重新从 OSS 获取最新状态
    new_id = crud._path_to_id(new_path)
    updated = crud.get_by_id(new_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="更新后文件不存在")
    return FileOut(**updated)


def copy_file(file_id: int, target_parent_id: int | None) -> FileOut:
    """复制文件/文件夹到目标文件夹。"""
    item = crud.get_by_id(file_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    src_path = item["path"].lstrip("/")
    dest_parent_key = _resolve_parent_key(target_parent_id)
    name = item["name"]

    # 检查目标位置是否有同名
    siblings = crud.list_by_parent(target_parent_id)
    dest_name = name
    # 如果目标已有同名，自动加后缀
    counter = 1
    while any(s["name"] == dest_name for s in siblings):
        base, _, ext = name.rpartition(".")
        if ext and base:
            dest_name = f"{base} ({counter}).{ext}"
        else:
            dest_name = f"{name} ({counter})"
        counter += 1

    dest_path = f"{dest_parent_key}/{dest_name}" if dest_parent_key else dest_name

    if item["type"] == "folder":
        all_items = crud.list_all()
        for node in all_items:
            node_path = node["path"].lstrip("/")
            if node_path.startswith(src_path + "/") or node_path == src_path:
                if node["type"] == "file":
                    rel = node_path[len(src_path):]
                    crud.copy_object(node_path, dest_path + rel)
    else:
        if crud.object_exists(src_path):
            crud.copy_object(src_path, dest_path)

    new_id = crud._path_to_id(dest_path)
    updated = crud.get_by_id(new_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="复制后文件不存在")
    return FileOut(**updated)


def generate_upload_token(body: UploadTokenRequest) -> UploadTokenOut:
    """生成前端直传 OSS 的预签名 URL。"""
    parent_key = _resolve_parent_key(body.parent_id)
    file_name = body.file_name.strip("/").replace("/", "_")  # 防止路径穿越

    # 检查同名文件
    siblings = crud.list_by_parent(body.parent_id)
    if any(s["name"] == file_name for s in siblings):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="同名文件已存在")

    key = f"{parent_key}/{file_name}" if parent_key else file_name
    result = crud.generate_presigned_upload_url(key, body.content_type, body.expire_seconds)
    return UploadTokenOut(**result)


def delete_file(file_id: int) -> None:
    """从 OSS 删除文件或文件夹（含子项）。"""
    item = crud.get_by_id(file_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    key = item["path"].lstrip("/")
    if item["type"] == "folder":
        crud.delete_prefix(key)
    else:
        if crud.object_exists(key):
            crud.delete_object(key)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
