from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RoleType(str, Enum):
    developer = "developer"
    designer = "designer"
    manager = "manager"
    marketer = "marketer"
    junior = "junior"


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Project(BaseModel):
    id: int
    title: str
    description: str
    required_skills: Optional[str] = ""


class User(BaseModel):
    id: int
    username: str
    email: str
    role: RoleType
    bio: Optional[str] = ""
    project: Optional[Project] = None
    skills: Optional[List[Skill]] = []
