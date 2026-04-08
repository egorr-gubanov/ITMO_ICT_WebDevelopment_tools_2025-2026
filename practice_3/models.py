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
    level: Optional[int] = None


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


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    role: RoleType
    bio: Optional[str] = ""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Optional[Project] = Relationship(back_populates="users")
    skills: List[Skill] = Relationship(back_populates="users", link_model=UserSkillLink)
