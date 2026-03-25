from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing_extensions import TypedDict

from app.connection import get_session
from app.models import (
    Project,
    ProjectDefault,
    ProjectPatch,
    ProjectWithTeams,
    Team,
    TeamMember,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreateResponse(TypedDict):
    status: int
    data: Project


class OkResponse(TypedDict):
    ok: bool


@router.get("/", response_model=List[Project])
def list_projects(session: Session = Depends(get_session)) -> List[Project]:
    return session.exec(select(Project)).all()


@router.get("/search", response_model=List[Project])
def search_projects(
    session: Session = Depends(get_session),
    status: Optional[str] = Query(default=None),
) -> List[Project]:
    stmt = select(Project)
    if status is not None:
        stmt = stmt.where(Project.status == status)
    return list(session.exec(stmt).all())


@router.get("/{project_id}", response_model=ProjectWithTeams)
def get_project(
    project_id: int, session: Session = Depends(get_session)
) -> Project:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.teams))
    )
    project = session.exec(stmt).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    return project


@router.post("/", response_model=ProjectCreateResponse)
def create_project(
    payload: ProjectDefault, session: Session = Depends(get_session)
) -> ProjectCreateResponse:
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return {"status": 200, "data": project}


@router.patch("/{project_id}", response_model=ProjectDefault)
def patch_project(
    project_id: int,
    patch: ProjectPatch,
    session: Session = Depends(get_session),
) -> ProjectDefault:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return ProjectDefault.model_validate(project)


@router.delete("/{project_id}", response_model=OkResponse)
def delete_project(
    project_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    teams = session.exec(
        select(Team).where(Team.project_id == project_id)
    ).all()
    for team in teams:
        for link in session.exec(
            select(TeamMember).where(TeamMember.team_id == team.id)
        ).all():
            session.delete(link)
        session.delete(team)
    session.delete(project)
    session.commit()
    return {"ok": True}
