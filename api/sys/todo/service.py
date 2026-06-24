from fastapi import HTTPException
from api.sys.todo import crud
from api.sys.todo.schema import TodoCreate, TodoUpdate, TodoOut, TodoListOut

def list_todos(user_id: int) -> TodoListOut:
    items = [TodoOut(**t) for t in crud.list_by_user(user_id)]
    return TodoListOut(total=len(items), items=items)

def create_todo(user_id: int, body: TodoCreate) -> TodoOut:
    return TodoOut(**crud.create(user_id, body.model_dump()))

def update_todo(todo_id: int, body: TodoUpdate) -> TodoOut:
    t = crud.update(todo_id, body.model_dump(exclude_unset=True))
    if not t:
        raise HTTPException(status_code=404, detail="待办不存在")
    return TodoOut(**t)

def delete_todo(todo_id: int) -> None:
    if not crud.delete(todo_id):
        raise HTTPException(status_code=404, detail="待办不存在")
