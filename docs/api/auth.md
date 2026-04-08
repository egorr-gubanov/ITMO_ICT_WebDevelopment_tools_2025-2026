# API: авторизация и профиль

Раздел объединяет публичные маршруты **`/auth`** и защищённые **`/me`** (требуется заголовок `Authorization: Bearer <JWT>`).  
Токен выдаётся эндпоинтом `POST /auth/token`; схема OAuth2 в Swagger: поле `tokenUrl` указывает на `/auth/token`.

Вспомогательная логика JWT и bcrypt: [`app/auth.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/auth.py).

---

## `POST /auth/register`

Описание: регистрация пользователя с хэшированием пароля.

**Body (JSON):** `RegisterRequest` — `username`, `email`, `password`, `role`, `bio` (опционально строкой).

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123","role":"developer","bio":""}'
```

**Пример ответа:** `200 OK` (пароль не возвращается)

```json
{
  "status": 200,
  "data": {
    "username": "alice",
    "email": "alice@example.com",
    "role": "developer",
    "bio": ""
  }
}
```

**Ошибка:** `400` если email уже занят: `{"detail":"Email already registered"}`.

**Код эндпоинта:**

```python
@router.post("/register", response_model=RegisterResponse)
def register(
    payload: RegisterRequest,
    session: Session = Depends(get_session),
) -> RegisterResponse:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        bio=payload.bio,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"status": 200, "data": UserDefault.model_validate(user)}
```

---

## `POST /auth/token`

Описание: вход; тело — **form-urlencoded** (`OAuth2PasswordRequestForm`: поля `username`, `password`). В поле `username` можно передать **логин или email**.

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

**Пример ответа:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ошибка:** `401` при неверных учётных данных.

**Код эндпоинта:**

```python
@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenResponse:
    user = authenticate_user(session, form_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## `GET /me/`

Описание: текущий пользователь с навыками.  
**Заголовок:** `Authorization: Bearer <access_token>`.

**Пример запроса:**

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -s http://127.0.0.1:8000/me/ -H "Authorization: Bearer $TOKEN"
```

**Пример ответа:** `200 OK` — объект `UserWithSkills`.

**Ошибки:** `401` при невалидном JWT (`Could not validate credentials`).

**Код эндпоинта:**

```python
@router.get("/", response_model=UserWithSkills)
def get_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.skills))
    )
    user = session.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

---

## `PATCH /me/`

Описание: частичное обновление своего профиля (`UserPatch`). Требуется Bearer-токен.

**Код эндпоинта:**

```python
@router.patch("/", response_model=UserWithSkills)
def patch_me(
    patch: UserPatch,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

---

## `POST /me/change-password`

Описание: смена пароля. **Body (JSON):** `old_password`, `new_password`.

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/me/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"secret123","new_password":"newSecret456"}'
```

**Пример ответа:** `200 OK` — `{"ok": true}`.

**Ошибка:** `400` — `Old password is incorrect`.

**Код эндпоинта:**

```python
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    if not verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.hashed_password = get_password_hash(payload.new_password)
    session.add(user)
    session.commit()
    return {"ok": True}
```

---

## `GET /me/teams`

Описание: команды, в которых состоит текущий пользователь (`List[Team]`).

**Код эндпоинта:**

```python
@router.get("/teams", response_model=List[Team])
def my_teams(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[Team]:
    stmt = (
        select(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
        .distinct()
    )
    return list(session.exec(stmt).all())
```

---

## `GET /me/projects`

Описание: проекты, в которых пользователь участвует через членство в команде (`List[Project]`).

**Код эндпоинта:**

```python
@router.get("/projects", response_model=List[Project])
def my_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[Project]:
    stmt = (
        select(Project)
        .join(Team, Project.id == Team.project_id)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
        .distinct()
    )
    return list(session.exec(stmt).all())
```
