from fastapi import APIRouter, Depends
from api.core.deps import get_current_user
from api.core.response import ApiResponse
from api.sys.team.schema import TeamCreate, TeamUpdate, TeamMemberUpdate
from api.sys.team import service

router = APIRouter(prefix="/sys/team", tags=["team"])


@router.get("", response_model=ApiResponse)
def list_teams(_: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.list_teams().model_dump())


@router.get("/{team_id}", response_model=ApiResponse)
def get_team(team_id: int, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.get_team(team_id).model_dump())


@router.post("", response_model=ApiResponse)
def create_team(body: TeamCreate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.create_team(body).model_dump(), message="创建成功")


@router.put("/{team_id}", response_model=ApiResponse)
def update_team(team_id: int, body: TeamUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_team(team_id, body).model_dump(), message="更新成功")


@router.put("/{team_id}/members", response_model=ApiResponse)
def update_members(team_id: int, body: TeamMemberUpdate, _: str = Depends(get_current_user)):
    return ApiResponse.ok(data=service.update_members(team_id, body).model_dump(), message="成员更新成功")


@router.delete("/{team_id}", response_model=ApiResponse)
def delete_team(team_id: int, _: str = Depends(get_current_user)):
    service.delete_team(team_id)
    return ApiResponse.ok(message="删除成功")
