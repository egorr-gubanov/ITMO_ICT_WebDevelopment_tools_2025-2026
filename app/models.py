from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class RoleType(str, Enum):
    developer = "developer"
    designer = "designer"
    manager = "manager"
    marketer = "marketer"
    junior = "junior"
    tester = "tester"
    devops = "devops"


class UserSkillLink(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key="user.id", primary_key=True)
    skill_id: Optional[int] = Field(foreign_key="skill.id", primary_key=True)
    proficiency_level: Optional[str] = Field(default="beginner")


class TeamMember(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key="user.id", primary_key=True)
    team_id: Optional[int] = Field(foreign_key="team.id", primary_key=True)
    member_role: Optional[str] = Field(default="member")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    role: RoleType
    bio: str = ""
    hashed_password: str = ""
    skills: List["Skill"] = Relationship(
        back_populates="users", link_model=UserSkillLink
    )
    teams: List["Team"] = Relationship(
        back_populates="members", link_model=TeamMember
    )


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
    required_skills: str = ""
    status: str = "open"
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    teams: List["Team"] = Relationship(back_populates="project")


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="teams")
    members: List["User"] = Relationship(
        back_populates="teams", link_model=TeamMember
    )


class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class SkillPatch(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectDefault(SQLModel):
    title: str
    description: str
    required_skills: Optional[str] = ""
    status: Optional[str] = "open"
    owner_id: Optional[int] = None


class TeamDefault(SQLModel):
    name: str
    description: Optional[str] = ""
    project_id: Optional[int] = None


class TeamPatch(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None


class UserDefault(SQLModel):
    username: str
    email: str
    role: RoleType
    bio: Optional[str] = ""


class UserPatch(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[RoleType] = None
    bio: Optional[str] = None


class ProjectPatch(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None


class UserWithSkills(UserDefault):
    skills: List[Skill] = []


class ProjectWithTeams(ProjectDefault):
    teams: List[Team] = []


class TeamWithMembers(TeamDefault):
    members: List[User] = []
