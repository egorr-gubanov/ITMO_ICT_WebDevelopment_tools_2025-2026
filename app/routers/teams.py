from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing_extensions import TypedDict

from app.connection import get_session
from app.models import Team, TeamDefault, TeamMember, TeamPatch, TeamWithMembers, User

router = APIRouter(prefix="/teams", tags=["Teams"])


class TeamCreateResponse(TypedDict):
    status: int
    data: Team


class OkResponse(TypedDict):
    ok: bool


@router.get("/", response_model=List[Team])
def list_teams(session: Session = Depends(get_session)) -> List[Team]:
    return session.exec(select(Team)).all()


@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(team_id: int, session: Session = Depends(get_session)) -> Team:
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members))
    )
    team = session.exec(stmt).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    return team


@router.post("/", response_model=TeamCreateResponse)
def create_team(
    payload: TeamDefault, session: Session = Depends(get_session)
) -> TeamCreateResponse:
    team = Team(**payload.model_dump())
    session.add(team)
    session.commit()
    session.refresh(team)
    return {"status": 200, "data": team}


@router.patch("/{team_id}", response_model=Team)
def patch_team(
    team_id: int,
    patch: TeamPatch,
    session: Session = Depends(get_session),
) -> Team:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(team, key, value)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/{team_id}", response_model=OkResponse)
def delete_team(team_id: int, session: Session = Depends(get_session)) -> OkResponse:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all():
        session.delete(link)
    session.delete(team)
    session.commit()
    return {"ok": True}


@router.post("/{team_id}/members/{user_id}", response_model=OkResponse)
def add_team_member(
    team_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    member_role: str = Query(default="member"),
) -> OkResponse:
    if session.get(Team, team_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    existing = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400, detail="User is already a member of this team"
        )
    link = TeamMember(
        team_id=team_id,
        user_id=user_id,
        member_role=member_role,
    )
    session.add(link)
    session.commit()
    return {"ok": True}


@router.delete("/{team_id}/members/{user_id}", response_model=OkResponse)
def remove_team_member(
    team_id: int, user_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    link = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
