# API: пользователи

Префикс роутера: `/users`. Базовый URL в примерах: `http://127.0.0.1:8000`.

---

## `GET /users/`

Описание: список всех пользователей.

| Тип параметра | Имя | Описание |
|---------------|-----|----------|
| — | — | — |

**Пример запроса:**

```http
GET /users/ HTTP/1.1
Host: 127.0.0.1:8000
```

```bash
curl -s http://127.0.0.1:8000/users/
```

**Пример ответа:** `200 OK`, тело — JSON-массив объектов `User`.

```json
[
  {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "role": "developer",
    "bio": "",
    "hashed_password": "$2b$12$..."
  }
]
```

**Код эндпоинта:**

```python
@router.get("/", response_model=List[User])
def list_users(session: Session = Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()
```

---

## `GET /users/search`

Описание: поиск пользователей с фильтрами по роли и/или названию навыка.

| Тип | Имя | Описание |
|-----|-----|----------|
| Query | `role` | Опционально. Значение `RoleType` (например `developer`). |
| Query | `skill` | Опционально. Точное имя навыка (например `Python`). |

**Пример запроса:**

```bash
curl -s "http://127.0.0.1:8000/users/search?role=developer&skill=Python"
```

**Пример ответа:** `200 OK`

```json
[
  {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "role": "developer",
    "bio": "",
    "hashed_password": "$2b$12$..."
  }
]
```

**Код эндпоинта:**

```python
@router.get("/search", response_model=List[User])
def search_users(
    session: Session = Depends(get_session),
    role: Optional[RoleType] = Query(default=None),
    skill: Optional[str] = Query(default=None, description="Skill name, e.g. Python"),
) -> List[User]:
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

---

## `GET /users/{user_id}`

Описание: один пользователь с подгруженными навыками (`UserWithSkills`).

| Тип | Имя | Описание |
|-----|-----|----------|
| Path | `user_id` | `int` |

**Пример запроса:**

```bash
curl -s http://127.0.0.1:8000/users/1
```

**Пример ответа:** `200 OK`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "role": "developer",
  "bio": "",
  "skills": [
    {
      "id": 1,
      "name": "Python",
      "description": ""
    }
  ]
}
```

**Ошибка:** `404` — `{"detail":"Not found"}`.

**Код эндпоинта:**

```python
@router.get("/{user_id}", response_model=UserWithSkills)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.skills))
    )
    user = session.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

---

## `POST /users/`

Описание: создание пользователя по схеме `UserDefault` (пароль не задаётся — для учётной записи с паролем используйте `/auth/register`).

| Тип | Имя | Описание |
|-----|-----|----------|
| Body | JSON | `UserDefault`: `username`, `email`, `role`, `bio` |

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@example.com","role":"designer","bio":""}'
```

**Пример ответа:** `200 OK`

```json
{
  "status": 200,
  "data": {
    "id": 2,
    "username": "bob",
    "email": "bob@example.com",
    "role": "designer",
    "bio": "",
    "hashed_password": ""
  }
}
```

**Код эндпоинта:**

```python
@router.post("/", response_model=UserCreateResponse)
def create_user(
    payload: UserDefault, session: Session = Depends(get_session)
) -> UserCreateResponse:
    user = User(**payload.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}
```

---

## `PATCH /users/{user_id}`

Описание: частичное обновление полей (`UserPatch`).

| Тип | Имя | Описание |
|-----|-----|----------|
| Path | `user_id` | `int` |
| Body | JSON | `UserPatch`: любое из `username`, `email`, `role`, `bio` |

**Пример запроса:**

```bash
curl -s -X PATCH http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"bio":"Backend developer"}'
```

**Пример ответа:** `200 OK`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "role": "developer",
  "bio": "Backend developer"
}
```

**Код эндпоинта:**

```python
@router.patch("/{user_id}", response_model=UserDefault)
def patch_user(
    user_id: int,
    patch: UserPatch,
    session: Session = Depends(get_session),
) -> UserDefault:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserDefault.model_validate(user)
```

---

## `DELETE /users/{user_id}`

Описание: удаление пользователя и связанных `UserSkillLink`, `TeamMember`.

| Тип | Имя | Описание |
|-----|-----|----------|
| Path | `user_id` | `int` |

**Пример запроса:**

```bash
curl -s -X DELETE http://127.0.0.1:8000/users/2
```

**Пример ответа:** `200 OK`

```json
{"ok": true}
```

**Код эндпоинта:**

```python
@router.delete("/{user_id}", response_model=OkResponse)
def delete_user(user_id: int, session: Session = Depends(get_session)) -> OkResponse:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all():
        session.delete(link)
    for link in session.exec(
        select(TeamMember).where(TeamMember.user_id == user_id)
    ).all():
        session.delete(link)
    session.delete(user)
    session.commit()
    return {"ok": True}
```

---

## `POST /users/{user_id}/skills/{skill_id}`

Описание: добавить связь пользователь–навык (`UserSkillLink`).

| Тип | Имя | Описание |
|-----|-----|----------|
| Path | `user_id`, `skill_id` | `int` |
| Query | `proficiency_level` | По умолчанию `beginner`. |

**Пример запроса:**

```bash
curl -s -X POST "http://127.0.0.1:8000/users/1/skills/1?proficiency_level=intermediate"
```

**Пример ответа:** `200 OK`

```json
{"ok": true}
```

**Код эндпоинта:**

```python
@router.post("/{user_id}/skills/{skill_id}", response_model=OkResponse)
def add_user_skill(
    user_id: int,
    skill_id: int,
    session: Session = Depends(get_session),
    proficiency_level: str = Query(default="beginner"),
) -> OkResponse:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    if session.get(Skill, skill_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    existing = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == skill_id,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400, detail="User already has this skill link"
        )
    link = UserSkillLink(
        user_id=user_id,
        skill_id=skill_id,
        proficiency_level=proficiency_level,
    )
    session.add(link)
    session.commit()
    return {"ok": True}
```

---

## `DELETE /users/{user_id}/skills/{skill_id}`

Описание: удалить связь пользователь–навык.

| Тип | Имя | Описание |
|-----|-----|----------|
| Path | `user_id`, `skill_id` | `int` |

**Пример запроса:**

```bash
curl -s -X DELETE http://127.0.0.1:8000/users/1/skills/1
```

**Пример ответа:** `200 OK`

```json
{"ok": true}
```

**Код эндпоинта:**

```python
@router.delete("/{user_id}/skills/{skill_id}", response_model=OkResponse)
def remove_user_skill(
    user_id: int, skill_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    link = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == skill_id,
        )
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
```

</think>
Исправляю опечатку в `docs/api/users.md` (лишний отступ в примере кода `delete_user`).

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace