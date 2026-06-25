"""OSS 对象存储 CRUD —— 从阿里云 OSS 获取真实数据。

OSS 是扁平的 key 结构，通过 '/' 分隔符模拟文件夹层级。
本模块将 OSS 的 key 列表转换为树形结构，并生成稳定的 ID。
"""
import zlib
from datetime import datetime
from typing import Optional

import oss2

from api.core.config import oss_settings

_bucket: Optional[oss2.Bucket] = None


def _get_bucket() -> oss2.Bucket:
    """懒加载 OSS Bucket 客户端"""
    global _bucket
    if _bucket is None:
        auth = oss2.Auth(oss_settings.access_key_id, oss_settings.access_key_secret)
        _bucket = oss2.Bucket(auth, oss_settings.endpoint, oss_settings.bucket_name)
    return _bucket


def _path_to_id(path: str) -> int:
    """将 OSS key 路径转换为稳定的整数 ID。"""
    return zlib.crc32(path.encode("utf-8"))


def _full_prefix() -> str:
    """获取配置的全局前缀。"""
    return oss_settings.prefix or ""


def _normalize_key(key: str) -> str:
    """去掉全局前缀后的相对路径。"""
    prefix = _full_prefix()
    if prefix and key.startswith(prefix):
        return key[len(prefix):]
    return key


def _build_url(key: str) -> str:
    """构建文件可访问 URL，始终包含协议。"""
    full_key = _full_prefix() + key
    if oss_settings.custom_domain:
        domain = oss_settings.custom_domain.rstrip("/")
        # 如果自定义域名没有协议，默认使用 https
        if not domain.startswith(("http://", "https://")):
            domain = f"https://{domain}"
        return f"{domain}/{full_key}"
    return f"https://{oss_settings.bucket_name}.{oss_settings.endpoint}/{full_key}"


def _guess_content_type(name: str) -> str:
    """根据文件名猜测 Content-Type。"""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    mapping = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "txt": "text/plain",
        "csv": "text/csv",
        "json": "application/json",
        "mp4": "video/mp4",
        "mp3": "audio/mpeg",
        "zip": "application/zip",
    }
    return mapping.get(ext, "application/octet-stream")


def _make_folder_node(folder_path: str) -> dict:
    """根据文件夹路径创建节点字典。"""
    rel = folder_path.rstrip("/")
    parts = rel.split("/")
    name = parts[-1]
    parent_rel = "/".join(parts[:-1])
    parent_id = _path_to_id(parent_rel + "/") if parent_rel else None
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": _path_to_id(folder_path),
        "name": name,
        "type": "folder",
        "path": "/" + rel,
        "parent_id": parent_id,
        "size": 0,
        "content_type": None,
        "url": None,
        "description": None,
        "created_at": ts,
        "updated_at": ts,
    }


def _parse_key_to_nodes(key: str, size: int, last_modified: datetime) -> list[dict]:
    """将一个 OSS key 拆解为路径上的所有节点（文件夹 + 文件）。"""
    if not key or key == _full_prefix():
        return []

    if key.endswith("/"):
        # 纯文件夹标记对象
        rel_key = _normalize_key(key).rstrip("/")
        if not rel_key:
            return []
        parts = rel_key.split("/")
        nodes = []
        for i in range(1, len(parts) + 1):
            folder_path = "/".join(parts[:i]) + "/"
            nodes.append(_make_folder_node(folder_path))
        return nodes

    rel_key = _normalize_key(key)
    parts = rel_key.split("/")
    nodes = []

    # 生成路径上所有文件夹节点
    for i in range(1, len(parts)):
        folder_path = "/".join(parts[:i]) + "/"
        nodes.append(_make_folder_node(folder_path))

    # 文件节点本身
    file_path = rel_key
    parent_rel = "/".join(parts[:-1])
    parent_id = _path_to_id(parent_rel + "/") if parent_rel else None
    name = parts[-1]
    ts = last_modified.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_modified, datetime) else str(last_modified)
    nodes.append({
        "id": _path_to_id(file_path),
        "name": name,
        "type": "file",
        "path": "/" + rel_key,
        "parent_id": parent_id,
        "size": size,
        "content_type": _guess_content_type(name),
        "url": _build_url(rel_key),
        "description": None,
        "created_at": ts,
        "updated_at": ts,
    })
    return nodes


# ---------------------------------------------------------------------------
#  公共 API
# ---------------------------------------------------------------------------

def list_all() -> list[dict]:
    """列出 OSS Bucket 中的所有对象，返回去重后的节点列表。"""
    bucket = _get_bucket()
    prefix = _full_prefix()

    node_map: dict[int, dict] = {}

    for obj in oss2.ObjectIterator(bucket, prefix=prefix, max_keys=1000):
        key = obj.key
        if not key or key == prefix:
            continue

        nodes = _parse_key_to_nodes(key, obj.size, obj.last_modified)
        for node in nodes:
            if node["id"] not in node_map:
                node_map[node["id"]] = node
            else:
                existing = node_map[node["id"]]
                if node["type"] == "file" and existing["type"] == "file":
                    node_map[node["id"]] = node

    return list(node_map.values())


def get_by_id(file_id: int) -> Optional[dict]:
    """通过 ID 获取节点（从全量列表中查找）。"""
    for node in list_all():
        if node["id"] == file_id:
            return node
    return None


def list_by_parent(parent_id: Optional[int] = None) -> list[dict]:
    """返回指定父级下的直接子项。"""
    items = [n for n in list_all() if n["parent_id"] == parent_id]
    items.sort(key=lambda x: (x["type"] != "folder", x["name"]))
    return items


def create_folder(key: str) -> dict:
    """在 OSS 中创建文件夹（创建一个以 '/' 结尾的空对象）。"""
    bucket = _get_bucket()
    folder_key = key.rstrip("/") + "/"
    full_key = _full_prefix() + folder_key
    bucket.put_object(full_key, b"")
    return _make_folder_node(folder_key)


def create_file(key: str, content: bytes, content_type: Optional[str] = None) -> dict:
    """上传文件到 OSS。"""
    bucket = _get_bucket()
    full_key = _full_prefix() + key
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    bucket.put_object(full_key, content, headers=headers)

    rel_key = _normalize_key(key)
    parts = rel_key.split("/")
    name = parts[-1]
    parent_rel = "/".join(parts[:-1])
    parent_id = _path_to_id(parent_rel + "/") if parent_rel else None
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": _path_to_id(rel_key),
        "name": name,
        "type": "file",
        "path": "/" + rel_key,
        "parent_id": parent_id,
        "size": len(content),
        "content_type": content_type or _guess_content_type(name),
        "url": _build_url(rel_key),
        "description": None,
        "created_at": ts,
        "updated_at": ts,
    }


def copy_object(src_key: str, dst_key: str) -> None:
    """在 OSS 中复制对象。"""
    bucket = _get_bucket()
    full_src = _full_prefix() + src_key
    full_dst = _full_prefix() + dst_key
    bucket.copy_object(oss_settings.bucket_name, full_src, full_dst)


def delete_object(key: str) -> None:
    """删除 OSS 中的单个对象。"""
    bucket = _get_bucket()
    full_key = _full_prefix() + key
    bucket.delete_object(full_key)


def delete_prefix(prefix: str) -> int:
    """递归删除指定前缀下的所有对象（删除文件夹）。"""
    bucket = _get_bucket()
    full_prefix = _full_prefix() + prefix.rstrip("/") + "/"
    count = 0
    for obj in oss2.ObjectIterator(bucket, prefix=full_prefix, max_keys=1000):
        bucket.delete_object(obj.key)
        count += 1
    return count


def object_exists(key: str) -> bool:
    """检查 OSS 对象是否存在。"""
    bucket = _get_bucket()
    full_key = _full_prefix() + key
    return bucket.object_exists(full_key)


def generate_presigned_upload_url(key: str, content_type: str, expire_seconds: int = 3600) -> dict:
    """生成前端直传 OSS 所需的预签名 PUT URL 及访问信息。

    返回:
        {
            "upload_url": "https://...预签名上传地址",
            "file_url":   "https://...上传完成后的文件访问地址",
            "key":        "相对路径 key",
            "expire":     过期时间戳(秒)
        }
    """
    import time
    bucket = _get_bucket()
    full_key = _full_prefix() + key

    # 生成预签名 PUT URL（允许前端直接上传）
    upload_url = bucket.sign_url(
        'PUT',
        full_key,
        expire_seconds,
        headers={'Content-Type': content_type},
    )

    return {
        "upload_url": upload_url,
        "file_url": _build_url(key),
        "key": key,
        "expire": int(time.time()) + expire_seconds,
    }
