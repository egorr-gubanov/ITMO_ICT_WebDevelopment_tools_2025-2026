from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from app.connection import get_session
from app.models import Skill, SkillDefault, SkillPatch, UserSkillLink

router = APIRouter(prefix="/skills", tags=["Skills"])


class SkillCreateResponse(TypedDict):
    status: int
    data: Skill


class OkResponse(TypedDict):
    ok: bool


@router.get("/", response_model=List[Skill])
def list_skills(session: Session = Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    return skill


@router.post("/", response_model=SkillCreateResponse)
def create_skill(
    payload: SkillDefault, session: Session = Depends(get_session)
) -> SkillCreateResponse:
    skill = Skill(**payload.model_dump())
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@router.patch("/{skill_id}", response_model=Skill)
def patch_skill(
    skill_id: int,
    patch: SkillPatch,
    session: Session = Depends(get_session),
) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(skill, key, value)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.delete("/{skill_id}", response_model=OkResponse)
def delete_skill(skill_id: int, session: Session = Depends(get_session)) -> OkResponse:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.skill_id == skill_id)
    ).all():
        session.delete(link)
    session.delete(skill)
    session.commit()
    return {"ok": True}
