from fastapi import HTTPException, status
from api.sys.team import crud
from api.sys.team.schema import TeamCreate, TeamUpdate, TeamMemberUpdate, TeamOut, TeamListOut


def _to_out(team: dict) -> TeamOut:
    return TeamOut(**team, member_count=len(team["user_ids"]))


def list_teams() -> TeamListOut:
    items = [_to_out(t) for t in crud.list_all()]
    return TeamListOut(total=len(items), items=items)


def get_team(team_id: int) -> TeamOut:
    team = crud.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
    return _to_out(team)


def create_team(body: TeamCreate) -> TeamOut:
    if crud.get_by_name(body.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="团队名称已存在")
    if crud.get_by_code(body.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="团队编码已存在")
    return _to_out(crud.create(body.model_dump()))


def update_team(team_id: int, body: TeamUpdate) -> TeamOut:
    team = crud.update(team_id, body.model_dump(exclude_unset=True))
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
    return _to_out(team)


def update_members(team_id: int, body: TeamMemberUpdate) -> TeamOut:
    team = crud.set_members(team_id, body.user_ids)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
    return _to_out(team)


def delete_team(team_id: int) -> None:
    if not crud.delete(team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
