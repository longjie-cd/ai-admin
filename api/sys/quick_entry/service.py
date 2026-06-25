from datetime import datetime
from fastapi import HTTPException, status
from api.sys.quick_entry import crud
from api.sys.quick_entry.schema import QuickEntryCreate, QuickEntryUpdate, QuickEntryOut, QuickEntryListOut


def _out(entry: dict) -> QuickEntryOut:
    return QuickEntryOut(**entry)


def list_entries() -> QuickEntryListOut:
    items = [_out(e) for e in crud.list_all()]
    return QuickEntryListOut(total=len(items), items=items)


def get_entry(entry_id: int) -> QuickEntryOut:
    entry = crud.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快捷入口不存在")
    return _out(entry)


def create_entry(body: QuickEntryCreate) -> QuickEntryOut:
    data = body.model_dump()
    data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _out(crud.create(data))


def update_entry(entry_id: int, body: QuickEntryUpdate) -> QuickEntryOut:
    entry = crud.update(entry_id, body.model_dump(exclude_unset=True))
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快捷入口不存在")
    return _out(entry)


def delete_entry(entry_id: int) -> None:
    if not crud.delete(entry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快捷入口不存在")


def list_entries_for_user(user: dict) -> QuickEntryListOut:
    all_entries = crud.list_all()
    filtered = []
    for entry in all_entries:
        auth_ids = entry.get("auth_ids") or []
        if not auth_ids:
            filtered.append(entry)
            continue
        auth_type = entry.get("auth_type", "user")
        if auth_type == "user" and user.get("id") in auth_ids:
            filtered.append(entry)
        elif auth_type == "team" and user.get("team_id") in auth_ids:
            filtered.append(entry)
        elif auth_type == "role" and any(rid in auth_ids for rid in user.get("role_ids", [])):
            filtered.append(entry)
    items = [_out(e) for e in filtered]
    return QuickEntryListOut(total=len(items), items=items)
