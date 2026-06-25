from datetime import datetime
from fastapi import HTTPException, status
from api.sys.announcement import crud
from api.sys.announcement.schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut, AnnouncementListOut
from api.sys.user import crud as user_crud
from api.sys.team import crud as team_crud
from api.sys.role import crud as role_crud
from api.sys.message import crud as message_crud


def _out(item: dict) -> AnnouncementOut:
    return AnnouncementOut(**item)


def _target_user_ids(target_type: str, target_ids: list[int]) -> set[int]:
    user_ids: set[int] = set()
    if not target_ids:
        for u in user_crud.list_users():
            user_ids.add(u["id"])
        return user_ids

    if target_type == "user":
        for uid in target_ids:
            if user_crud.get_user_by_id(uid):
                user_ids.add(uid)
    elif target_type == "team":
        for tid in target_ids:
            team = team_crud.get_by_id(tid)
            if team:
                user_ids.update(team.get("user_ids", []))
    elif target_type == "role":
        all_users = user_crud.list_users()
        for rid in target_ids:
            role = role_crud.get_by_id(rid)
            if not role:
                continue
            for user in all_users:
                if rid in user.get("role_ids", []):
                    user_ids.add(user["id"])
    return user_ids


def _push_messages(announcement: dict) -> None:
    if not announcement.get("push_message"):
        return
    user_ids = _target_user_ids(announcement.get("target_type", "user"), announcement.get("target_ids") or [])
    link = f"/sys/announcement/{announcement['id']}"
    title = announcement.get("title", "")
    for uid in user_ids:
        message_crud.create({
            "user_id": uid,
            "title": f"公告：{title}",
            "content": announcement.get("content", "")[:200],
            "type": "info",
            "link": link,
        })


def list_announcements() -> AnnouncementListOut:
    items = [_out(a) for a in crud.list_all()]
    return AnnouncementListOut(total=len(items), items=items)


def get_announcement(announcement_id: int) -> AnnouncementOut:
    item = crud.get_by_id(announcement_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")
    return _out(item)


def create_announcement(body: AnnouncementCreate, author_id: int) -> AnnouncementOut:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = body.model_dump()
    data["author_id"] = author_id
    data["created_at"] = now
    data["updated_at"] = now
    item = crud.create(data)
    _push_messages(item)
    return _out(item)


def update_announcement(announcement_id: int, body: AnnouncementUpdate) -> AnnouncementOut:
    item = crud.update(announcement_id, {**body.model_dump(exclude_unset=True), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")
    _push_messages(item)
    return _out(item)


def delete_announcement(announcement_id: int) -> None:
    if not crud.delete(announcement_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")


def list_announcements_for_user(user: dict) -> AnnouncementListOut:
    all_items = crud.list_all()
    filtered = []
    user_id = user.get("id")
    team_id = user.get("team_id")
    role_ids = user.get("role_ids", [])

    for item in all_items:
        target_ids = item.get("target_ids") or []
        if not target_ids:
            filtered.append(item)
            continue
        target_type = item.get("target_type", "user")
        if target_type == "user" and user_id in target_ids:
            filtered.append(item)
        elif target_type == "team" and team_id in target_ids:
            filtered.append(item)
        elif target_type == "role" and any(rid in target_ids for rid in role_ids):
            filtered.append(item)

    items = [_out(a) for a in filtered]
    return AnnouncementListOut(total=len(items), items=items)
