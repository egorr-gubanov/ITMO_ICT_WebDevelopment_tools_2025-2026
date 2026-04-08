from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing_extensions import TypedDict

from practice_2.connection import get_session, init_db
from practice_2.models import (
    Project,
    ProjectDefault,
    ProjectPatch,
    Skill,
    SkillDefault,
    User,
    UserDefault,
    UserPatch,
    UserSkillLink,
    UserWithRelations,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class UserResponse(TypedDict):
    status: int
    data: User


class SkillResponse(TypedDict):
    status: int
    data: Skill


class ProjectResponse(TypedDict):
    status: int
    data: Project


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "Practice 2: SQLModel + PostgreSQL"


@app.get("/users")
def users_list(session: Session = Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@app.get("/user/{user_id}", response_model=UserWithRelations)
def user_get(user_id: int, session: Session = Depends(get_session)) -> User:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.project), selectinload(User.skills))
    )
    user = session.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/user")
def user_create(user: UserDefault, session: Session = Depends(get_session)) -> UserResponse:
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"status": 200, "data": db_user}


@app.patch("/user/{user_id}")
def user_patch(
    user_id: int,
    user: UserPatch,
    session: Session = Depends(get_session),
) -> UserDefault:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserDefault.model_validate(db_user)


@app.delete("/user/delete/{user_id}")
def user_delete(user_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all():
        session.delete(link)
    session.delete(db_user)
    session.commit()
    return {"ok": True}


@app.get("/skills")
def skills_list(session: Session = Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}")
def skill_get(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.post("/skill")
def skill_create(
    skill: SkillDefault, session: Session = Depends(get_session)
) -> SkillResponse:
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return {"status": 200, "data": db_skill}


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    db_skill = session.get(Skill, skill_id)
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.skill_id == skill_id)
    ).all():
        session.delete(link)
    session.delete(db_skill)
    session.commit()
    return {"ok": True}


@app.get("/projects")
def projects_list(session: Session = Depends(get_session)) -> List[Project]:
    return session.exec(select(Project)).all()


@app.get("/project/{project_id}")
def project_get(project_id: int, session: Session = Depends(get_session)) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/project")
def project_create(
    project: ProjectDefault, session: Session = Depends(get_session)
) -> ProjectResponse:
    db_project = Project.model_validate(project)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return {"status": 200, "data": db_project}


@app.patch("/project/{project_id}")
def project_patch(
    project_id: int, project: ProjectPatch, session: Session = Depends(get_session)
) -> ProjectDefault:
    db_project = session.get(Project, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    data = project.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_project, key, value)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return ProjectDefault.model_validate(db_project)


@app.delete("/project/delete/{project_id}")
def project_delete(
    project_id: int, session: Session = Depends(get_session)
) -> dict[str, bool]:
    db_project = session.get(Project, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for user in session.exec(select(User).where(User.project_id == project_id)).all():
        user.project_id = None
        session.add(user)
    session.delete(db_project)
    session.commit()
    return {"ok": True}


@app.post("/user/{user_id}/skill/{skill_id}")
def add_user_skill(
    user_id: int,
    skill_id: int,
    proficiency_level: str = "beginner",
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if session.get(Skill, skill_id) is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    link = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id, UserSkillLink.skill_id == skill_id
        )
    ).first()
    if link is not None:
        raise HTTPException(status_code=400, detail="Link already exists")
    session.add(
        UserSkillLink(
            user_id=user_id, skill_id=skill_id, proficiency_level=proficiency_level
        )
    )
    session.commit()
    return {"ok": True}


@app.delete("/user/{user_id}/skill/{skill_id}")
def remove_user_skill(
    user_id: int, skill_id: int, session: Session = Depends(get_session)
) -> dict[str, bool]:
    link = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id, UserSkillLink.skill_id == skill_id
        )
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
