from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing_extensions import TypedDict

from app.connection import get_session
from app.models import (
    RoleType,
    Skill,
    TeamMember,
    User,
    UserDefault,
    UserPatch,
    UserSkillLink,
    UserWithSkills,
)

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreateResponse(TypedDict):
    status: int
    data: User


class OkResponse(TypedDict):
    ok: bool


@router.get("/", response_model=List[User])
def list_users(session: Session = Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@router.get("/search", response_model=List[User])
def search_users(
    session: Session = Depends(get_session),
    role: Optional[RoleType] = Query(default=None),
    skill: Optional[str] = Query(default=None, description="Skill name, e.g. Python"),
) -> List[User]:
    stmt = select(User)
    if skill is not None:
        stmt = (
            stmt.join(UserSkillLink, User.id == UserSkillLink.user_id)
            .join(Skill, UserSkillLink.skill_id == Skill.id)
            .where(Skill.name == skill)
        )
    if role is not None:
        stmt = stmt.where(User.role == role)
    if skill is not None:
        stmt = stmt.distinct()
    return list(session.exec(stmt).all())


@router.get("/{user_id}", response_model=UserWithSkills)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.skills))
    )
    user = session.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.post("/", response_model=UserCreateResponse)
def create_user(
    payload: UserDefault, session: Session = Depends(get_session)
) -> UserCreateResponse:
    user = User(**payload.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}


@router.patch("/{user_id}", response_model=UserDefault)
def patch_user(
    user_id: int,
    patch: UserPatch,
    session: Session = Depends(get_session),
) -> UserDefault:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserDefault.model_validate(user)


@router.delete("/{user_id}", response_model=OkResponse)
def delete_user(user_id: int, session: Session = Depends(get_session)) -> OkResponse:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all():
        session.delete(link)
    for link in session.exec(
        select(TeamMember).where(TeamMember.user_id == user_id)
    ).all():
        session.delete(link)
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.post("/{user_id}/skills/{skill_id}", response_model=OkResponse)
def add_user_skill(
    user_id: int,
    skill_id: int,
    session: Session = Depends(get_session),
    proficiency_level: str = Query(default="beginner"),
) -> OkResponse:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    if session.get(Skill, skill_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    existing = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == skill_id,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400, detail="User already has this skill link"
        )
    link = UserSkillLink(
        user_id=user_id,
        skill_id=skill_id,
        proficiency_level=proficiency_level,
    )
    session.add(link)
    session.commit()
    return {"ok": True}


@router.delete("/{user_id}/skills/{skill_id}", response_model=OkResponse)
def remove_user_skill(
    user_id: int, skill_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    link = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == skill_id,
        )
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
