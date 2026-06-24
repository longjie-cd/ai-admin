from fastapi import APIRouter, Depends
from api.core.deps import get_current_user, get_current_user_obj
from api.core.response import ApiResponse
from api.sys.todo.schema import TodoCreate, TodoUpdate
from api.sys.todo import service

router = APIRouter(prefix="/sys/todo", tags=["todo"])

@router.get("", response_model=ApiResponse)
def list_todos(current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.list_todos(current_user["id"]).model_dump())

@router.post("", response_model=ApiResponse)
def create_todo(body: TodoCreate, current_user=Depends(get_current_user_obj)):
    return ApiResponse.ok(data=service.create_todo(current_user["id"], body).model_dump(), message="创建成功")

@router.put("/{todo_id}", response_model=ApiResponse)
def update_todo(todo_id: int, body: TodoUpdate, _=Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_todo(todo_id, body).model_dump(), message="更新成功")

@router.delete("/{todo_id}", response_model=ApiResponse)
def delete_todo(todo_id: int, _=Depends(get_current_user)):
    service.delete_todo(todo_id)
    return ApiResponse.ok(message="删除成功")
