from fastapi import HTTPException, status
from api.sys.message import crud
from api.sys.message.schema import MessageCreate, MessageUpdate, MessageOut, MessageListOut
from api.sys.user import crud as user_crud
from api.sys.team import crud as team_crud

def list_messages(user_id: int) -> MessageListOut:
    items = [MessageOut(**m) for m in crud.list_by_user(user_id)]
    return MessageListOut(total=len(items), items=items)

def get_message(msg_id: int) -> MessageOut:
    m = crud.get_by_id(msg_id)
    if not m:
        raise HTTPException(status_code=404, detail="消息不存在")
    return MessageOut(**m)

def create_message(body: MessageCreate) -> MessageOut:
    payload = body.model_dump()
    scope = payload.pop("send_scope", "user")
    payload.pop("team_id", None)

    if scope == "user":
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="请选择接收用户")
        if not user_crud.get_user_by_id(user_id):
            raise HTTPException(status_code=404, detail="接收用户不存在")
        return MessageOut(**crud.create(payload))

    if scope == "team":
        team_id = body.team_id
        if not team_id:
            raise HTTPException(status_code=400, detail="请选择接收团队")
        team = team_crud.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="接收团队不存在")
        user_ids = team.get("user_ids", [])
        if not user_ids:
            raise HTTPException(status_code=400, detail="该团队下暂无成员")
        first_created = None
        for user_id in user_ids:
            created = crud.create({**payload, "user_id": user_id})
            if first_created is None:
                first_created = created
        return MessageOut(**first_created)

    if scope == "all":
        users = user_crud.list_users()
        if not users:
            raise HTTPException(status_code=400, detail="暂无可接收消息的用户")
        first_created = None
        for user in users:
            created = crud.create({**payload, "user_id": user["id"]})
            if first_created is None:
                first_created = created
        return MessageOut(**first_created)

    raise HTTPException(status_code=400, detail="不支持的发送范围")

def update_message(msg_id: int, body: MessageUpdate) -> MessageOut:
    m = crud.update(msg_id, body.model_dump(exclude_unset=True))
    if not m:
        raise HTTPException(status_code=404, detail="消息不存在")
    return MessageOut(**m)

def mark_all_read(user_id: int) -> int:
    return crud.mark_all_read(user_id)

def delete_message(msg_id: int) -> None:
    if not crud.delete(msg_id):
        raise HTTPException(status_code=404, detail="消息不存在")

def unread_count(user_id: int) -> int:
    return crud.unread_count(user_id)
