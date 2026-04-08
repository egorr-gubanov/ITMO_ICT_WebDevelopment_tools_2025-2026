from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import get_current_user, get_password_hash, verify_password
from app.connection import get_session
from app.models import Project, Team, TeamMember, User, UserPatch, UserWithSkills

router = APIRouter(prefix="/me", tags=["Profile"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.get("/", response_model=UserWithSkills)
def get_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.skills))
    )
    user = session.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.patch("/", response_model=UserWithSkills)
def patch_me(
    patch: UserPatch,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    if not verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.hashed_password = get_password_hash(payload.new_password)
    session.add(user)
    session.commit()
    return {"ok": True}


@router.get("/teams", response_model=List[Team])
def my_teams(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[Team]:
    stmt = (
        select(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
        .distinct()
    )
    return list(session.exec(stmt).all())


@router.get("/projects", response_model=List[Project])
def my_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[Project]:
    stmt = (
        select(Project)
        .join(Team, Project.id == Team.project_id)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
        .distinct()
    )
    return list(session.exec(stmt).all())
