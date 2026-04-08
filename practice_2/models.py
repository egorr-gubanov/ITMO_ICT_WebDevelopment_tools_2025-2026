from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class RoleType(str, Enum):
    developer = "developer"
    designer = "designer"
    manager = "manager"
    marketer = "marketer"
    junior = "junior"


class UserSkillLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    proficiency_level: Optional[str] = "beginner"


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    users: List["User"] = Relationship(
        back_populates="skills", link_model=UserSkillLink
    )


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    required_skills: Optional[str] = ""
    users: List["User"] = Relationship(back_populates="project")


class UserDefault(SQLModel):
    username: str
    email: str
    role: RoleType
    bio: Optional[str] = ""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")


class UserPatch(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[RoleType] = None
    bio: Optional[str] = None
    project_id: Optional[int] = None


class User(UserDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: Optional[Project] = Relationship(back_populates="users")
    skills: List[Skill] = Relationship(back_populates="users", link_model=UserSkillLink)


class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class ProjectDefault(SQLModel):
    title: str
    description: str
    required_skills: Optional[str] = ""


class ProjectPatch(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None


class UserWithRelations(UserDefault):
    project: Optional[Project] = None
    skills: List[Skill] = []
