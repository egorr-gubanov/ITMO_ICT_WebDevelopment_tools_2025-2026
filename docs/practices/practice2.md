# Практика 2 — SQLModel и ORM (модели, связи, запросы)

Цель практики: научиться описывать таблицы в БД через SQLModel, настроить подключение к PostgreSQL и реализовать запросы/CRUD с использованием ORM (вместо “ручных” SQL).

В этом проекте ORM используется для хранения:

- пользователей (`user`)
- навыков (`skill`)
- проектов (`project`)
- команд (`team`)
- связей many-to-many:
  - `UserSkillLink` (пользователь ↔ навык) с полем `proficiency_level`
  - `TeamMember` (пользователь ↔ команда) с полем `member_role`

## 1) Подключение к БД (SQLModel → SQLAlchemy)

Подключение реализовано в [`app/connection.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/connection.py).

Ключевые части:

```python
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

Дальше `get_session` используется как dependency в роутерах:

```python
session: Session = Depends(get_session)
```

## 2) Создание моделей SQLModel

Главный файл моделей — [`app/models.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/models.py).

### 2.1) Перечисление ролей

`RoleType` хранится как enum PostgreSQL (`roletype`), что видно в миграциях (инициализация и расширение значений).

### 2.2) Many-to-many с ассоциативной сущностью и доп. полем

Ассоциативная сущность `UserSkillLink`:

```python
class UserSkillLink(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key="user.id", primary_key=True)
    skill_id: Optional[int] = Field(foreign_key="skill.id", primary_key=True)
    proficiency_level: Optional[str] = Field(default="beginner")
```

Ассоциативная сущность `TeamMember`:

```python
class TeamMember(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key="user.id", primary_key=True)
    team_id: Optional[int] = Field(foreign_key="team.id", primary_key=True)
    member_role: Optional[str] = Field(default="member")
```

`User` связывается с `Skill` и `Team` через link-модели:

```python
class User(SQLModel, table=True):
    skills: List["Skill"] = Relationship(
        back_populates="users", link_model=UserSkillLink
    )
    teams: List["Team"] = Relationship(
        back_populates="members", link_model=TeamMember
    )
```

### 2.3) One-to-many: Project → Team

Проект может иметь много команд.

В `Team` хранится внешний ключ `project_id`:

```python
class Team(SQLModel, table=True):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="teams")
```

А `Project` хранит коллекцию команд:

```python
class Project(SQLModel, table=True):
    teams: List["Team"] = Relationship(back_populates="project")
```

## 3) Запросы ORM и обновление данных

### 3.1) Фильтрация с join’ами (пример: поиск пользователей по роли/навыку)

Эндпоинт реализован в [`app/routers/users.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/routers/users.py) как `GET /users/search`.

Ключевая часть:

```python
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
```

### 3.2) Подгрузка связанных сущностей (selectinload)

Чтобы ответ `GET /users/{user_id}` включал навыки, используется:

```python
.options(selectinload(User.skills))
```

Аналогично для проекта:

```python
.options(selectinload(Project.teams))
```

### 3.3) CRUD с PATCH (частичное обновление)

Для частичного обновления используются `UserPatch`, `ProjectPatch`, `TeamPatch`:

- в запросе входные поля опциональны
- в теле обновляются только те поля, которые пришли

## Практическое задание (как это соответствует твоей сдаче)

По сути, я выполнил требования практики:

1. Настроил подключение к PostgreSQL и dependency `get_session`.
2. Реализовал модели SQLModel с primary keys и foreign keys.
3. Добавил both one-to-many (Project → Team) и many-to-many (User ↔ Skill, User ↔ Team) с ассоциативными link-таблицами и дополнительными полями.
4. Обновил эндпоинты под ORM:
   - запросы через `select()` + `where()` / `join()`
   - подгрузка связей через `selectinload()`

