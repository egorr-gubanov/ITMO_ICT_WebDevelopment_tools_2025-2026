from fastapi import FastAPI, HTTPException
from typing_extensions import TypedDict

from practice_1.models import Project, RoleType, Skill, User

app = FastAPI()


class UserResponse(TypedDict):
    status: int
    data: User


class ProjectResponse(TypedDict):
    status: int
    data: Project


class SkillResponse(TypedDict):
    status: int
    data: Skill


temp_users: list[User] = [
    User(
        id=1,
        username="alice_dev",
        email="alice@example.com",
        role=RoleType.developer,
        bio="Backend developer",
        project=Project(
            id=1,
            title="TeamFinder API",
            description="API for finding teammates",
            required_skills="Python, PostgreSQL",
        ),
        skills=[
            Skill(id=1, name="Python", description="FastAPI, asyncio"),
            Skill(id=2, name="PostgreSQL", description="DB schema and queries"),
        ],
    ),
    User(
        id=2,
        username="bob_ui",
        email="bob@example.com",
        role=RoleType.designer,
        bio="UI/UX designer",
        project=None,
        skills=[Skill(id=3, name="Figma", description="Prototyping and design")],
    ),
]

temp_projects: list[Project] = [
    Project(
        id=1,
        title="TeamFinder API",
        description="API for finding teammates",
        required_skills="Python, PostgreSQL",
    ),
    Project(
        id=2,
        title="Landing page",
        description="Public project landing",
        required_skills="Figma, Frontend",
    ),
]

temp_skills: list[Skill] = [
    Skill(id=1, name="Python", description="FastAPI, asyncio"),
    Skill(id=2, name="PostgreSQL", description="DB schema and queries"),
    Skill(id=3, name="Figma", description="Prototyping and design"),
]


def _user_index(user_id: int) -> int | None:
    for i, user in enumerate(temp_users):
        if user.id == user_id:
            return i
    return None


def _project_index(project_id: int) -> int | None:
    for i, project in enumerate(temp_projects):
        if project.id == project_id:
            return i
    return None


def _skill_index(skill_id: int) -> int | None:
    for i, skill in enumerate(temp_skills):
        if skill.id == skill_id:
            return i
    return None


@app.get("/")
def hello() -> str:
    return "Practice 1: TeamFinder temp API"


@app.get("/users")
def users_list() -> list[User]:
    return temp_users


@app.get("/user/{user_id}")
def user_by_id(user_id: int) -> list[User]:
    idx = _user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    return [temp_users[idx]]


@app.post("/user")
def user_create(user: User) -> UserResponse:
    if _user_index(user.id) is not None:
        raise HTTPException(status_code=400, detail="User with this id already exists")
    temp_users.append(user)
    return {"status": 200, "data": user}


@app.put("/user/{user_id}")
def user_update(user_id: int, user: User) -> list[User]:
    idx = _user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    temp_users[idx] = user
    return temp_users


@app.delete("/user/delete/{user_id}")
def user_delete(user_id: int) -> dict[str, str | int]:
    idx = _user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    temp_users.pop(idx)
    return {"status": 201, "message": "deleted"}


@app.get("/projects")
def projects_list() -> list[Project]:
    return temp_projects


@app.get("/project/{project_id}")
def project_by_id(project_id: int) -> list[Project]:
    idx = _project_index(project_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return [temp_projects[idx]]


@app.post("/project")
def project_create(project: Project) -> ProjectResponse:
    if _project_index(project.id) is not None:
        raise HTTPException(
            status_code=400, detail="Project with this id already exists"
        )
    temp_projects.append(project)
    return {"status": 200, "data": project}


@app.put("/project/{project_id}")
def project_update(project_id: int, project: Project) -> list[Project]:
    idx = _project_index(project_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Project not found")
    temp_projects[idx] = project
    return temp_projects


@app.delete("/project/delete/{project_id}")
def project_delete(project_id: int) -> dict[str, str | int]:
    idx = _project_index(project_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Project not found")
    temp_projects.pop(idx)
    return {"status": 201, "message": "deleted"}


@app.get("/skills")
def skills_list() -> list[Skill]:
    return temp_skills


@app.get("/skill/{skill_id}")
def skill_by_id(skill_id: int) -> list[Skill]:
    idx = _skill_index(skill_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return [temp_skills[idx]]


@app.post("/skill")
def skill_create(skill: Skill) -> SkillResponse:
    if _skill_index(skill.id) is not None:
        raise HTTPException(status_code=400, detail="Skill with this id already exists")
    temp_skills.append(skill)
    return {"status": 200, "data": skill}


@app.put("/skill/{skill_id}")
def skill_update(skill_id: int, skill: Skill) -> list[Skill]:
    idx = _skill_index(skill_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    temp_skills[idx] = skill
    return temp_skills


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int) -> dict[str, str | int]:
    idx = _skill_index(skill_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    temp_skills.pop(idx)
    return {"status": 201, "message": "deleted"}
