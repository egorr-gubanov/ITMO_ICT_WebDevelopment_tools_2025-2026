# Практика 1 — базовое FastAPI-приложение, аннотации и документирование

Цель практики: создать серверное приложение на FastAPI, реализовать набор HTTP-эндпоинтов (CRUD) и добиться корректного документирования через OpenAPI/Swagger. В проекте это реализовано как REST API для платформы поиска людей в команды.

## Что было сделано в проекте

### 1) Стартовое FastAPI-приложение

Основной вход приложения — [`app/main.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/main.py).

Ключевой момент: я использую `lifespan` для инициализации схемы в базе при старте сервера.

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
```

Роутеры подключены через `app.include_router(...)`, поэтому все эндпоинты группируются по логике предметной области:

- `app/routers/users.py`
- `app/routers/skills.py`
- `app/routers/projects.py`
- `app/routers/teams.py`
- `app/routers/auth.py` (регистрация/токен)
- `app/routers/me.py` (защищённый профиль)

### 2) CRUD-эндпоинты (на примере пользователей)

Роутер пользователей — [`app/routers/users.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/routers/users.py).

Например, метод получения списка пользователей:

```python
@router.get("/", response_model=List[User])
def list_users(session: Session = Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()
```

Создание пользователя:

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

Частичное обновление через `PATCH`:

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

### 3) Аннотирование и документирование

Чтобы FastAPI корректно строил документацию, я использую:

- `response_model` в эндпоинтах
- модели запросов/ответов на базе SQLModel:
  - `UserDefault`, `UserPatch`
  - `SkillDefault`, `SkillPatch`
  - `ProjectDefault`, `ProjectPatch`
  - `TeamDefault`, `TeamPatch`
- корректные типы входа/выхода в сигнатурах функций (например, `-> List[User]`).

В результате после запуска можно открыть Swagger UI:

- `GET /docs` — интерактивная документация
- `GET /openapi.json` — исходная схема API

### 4) Авторизация и профиль (добавлено к практике)

Чтобы платформа была защищённой, я добавил JWT-аутентификацию:

- регистрация: `POST /auth/register` в [`app/routers/auth.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/routers/auth.py)
- выдача токена: `POST /auth/token` (OAuth2PasswordRequestForm)
- защищённые эндпоинты профиля: `GET/PATCH /me/` и `POST /me/change-password` в [`app/routers/me.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/routers/me.py)

Механика JWT реализована в [`app/auth.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/auth.py).

## Результат практики

После выполнения практики у проекта есть:

- работающий FastAPI сервер (`app/main.py`)
- отдельные роутеры и группировка эндпоинтов по сущностям
- корректно документированные запросы/ответы (OpenAPI + Swagger)
- полноценный CRUD по доменным сущностям и добавленная авторизация.

