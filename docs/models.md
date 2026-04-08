# Модели данных

Имена таблиц в PostgreSQL по умолчанию совпадают с именами классов SQLModel в нижнем регистре: `user`, `skill`, `project`, `team`, `userskilllink`, `teammember`. Перечисление `RoleType` хранится как тип `ENUM` в PostgreSQL (`roletype`).

---

## Таблица `user`

| Поле | Тип в Python / БД | Описание |
|------|-------------------|----------|
| `id` | `int` (PK, autoincrement) | Идентификатор |
| `username` | `str` | Логин |
| `email` | `str` | Email |
| `role` | `RoleType` (enum) | Роль на платформе |
| `bio` | `str` | О себе |
| `hashed_password` | `str` | Bcrypt-хэш пароля |

**Связи:**

- Many-to-many с `skill` через `userskilllink` (`skills`, поле связи `proficiency_level`).
- Many-to-many с `team` через `teammember` (`teams`, поле связи `member_role`).
- One-to-many как владелец: на `project` ссылается `owner_id` (другие таблицы).

---

## Таблица `skill`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `int` (PK) | Идентификатор |
| `name` | `str` | Название навыка |
| `description` | `str`, опционально | Описание |

**Связи:** many-to-many с `user` через `userskilllink`.

---

## Таблица `project`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `int` (PK) | Идентификатор |
| `title` | `str` | Название |
| `description` | `str` | Описание |
| `required_skills` | `str` | Требуемые навыки (текст) |
| `status` | `str` | Статус (`open`, …) |
| `owner_id` | `int`, FK → `user.id`, nullable | Владелец проекта |

**Связи:** one-to-many к `team` (`teams`).

---

## Таблица `team`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `int` (PK) | Идентификатор |
| `name` | `str` | Название команды |
| `description` | `str`, optional | Описание |
| `project_id` | `int`, FK → `project.id`, nullable | Проект |

**Связи:**

- Many-to-one: `project`.
- Many-to-many с `user` через `teammember` (`members`, `member_role`).

---

## Таблица `userskilllink` (ассоциативная)

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | `int`, PK, FK → `user.id` | Пользователь |
| `skill_id` | `int`, PK, FK → `skill.id` | Навык |
| `proficiency_level` | `str`, default `"beginner"` | Уровень владения |

---

## Таблица `teammember` (ассоциативная)

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | `int`, PK, FK → `user.id` | Участник |
| `team_id` | `int`, PK, FK → `team.id` | Команда |
| `member_role` | `str`, default `"member"` | Роль в команде (lead, member, mentor) |

---

## Полный код моделей SQLModel

Файл [`app/models.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/models.py):

```python
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
```

---

## Подключение к БД (`connection.py`)

Файл [`app/connection.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/connection.py):

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

db_url = os.getenv("DB_URL", "postgresql://postgres:123@localhost/teamfinder_db")
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```
