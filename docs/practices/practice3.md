# Практика 3 — миграции Alembic, ENV, GitIgnore и структура проекта

Цель практики: настроить безопасное изменение структуры БД через миграции Alembic, подключить переменные окружения (.env) и правильно организовать репозиторий через `.gitignore`.

## 1) Alembic: цель и интеграция с SQLModel

В проекте Alembic интегрирован с SQLModel через метаданные.

Файл окружения:
[`migrations/env.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/migrations/env.py)

Ключевые идеи:

- target_metadata берется из `SQLModel.metadata`
- Alembic должен “видеть” модели, поэтому в `env.py` импортируются классы из `app.models`

## 2) Какие миграции были выполнены

### 2.1) Базовая миграция: пользователи/навыки/проекты

Файл:
`migrations/versions/d4b554615e44_initial_migration_users_skills_projects.py`

Он создал:

- таблицы `project`, `skill`, `user`
- ассоциативную таблицу `userskilllink`
- enum `roletype` (первичный набор значений)

### 2.2) Полная модель данных (добавление команд и связей)

Файл:
`migrations/versions/dcc627f340f5_full_data_model.py`

В этой миграции добавлены:

- таблица `team`
- таблица `teammember` (ассоциативная сущность с дополнительным полем `member_role`)
- колонка `project.status`
- колонка `user.hashed_password`
- удаление `user.project_id` (переход к связке через команды)

Ключевой фрагмент:

```python
op.create_table('team', ...)
op.create_table('teammember', ...)
op.add_column('project', sa.Column('status', ..., server_default='open'))
op.add_column('user', sa.Column('hashed_password', ..., server_default=''))
op.drop_column('user', 'project_id')
```

Также были расширены значения enum `roletype`:

```sql
ALTER TYPE roletype ADD VALUE IF NOT EXISTS 'tester'
ALTER TYPE roletype ADD VALUE IF NOT EXISTS 'devops'
```

### 2.3) Дополнение: `hashed_password` в `user`

Файл:
`migrations/versions/9c7c3cebacca_add_hashed_password_to_user.py`

Эта миграция оказалась пустой (`pass`), потому что поле `hashed_password` уже появилось в предыдущей миграции `dcc627f340f5_full_data_model.py`.

## 3) Переменные окружения (.env)

Файл:
[`/.env`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/.env)

Используются:

- `DB_URL` — строка подключения к PostgreSQL (в [`app/connection.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/connection.py))
- `SECRET_KEY` — ключ для JWT (в [`app/auth.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/auth.py))

Пример:

```env
DB_URL=postgresql://postgres:123@localhost/teamfinder_db
SECRET_KEY=super-secret-jwt-key-change-in-production-min-32-chars
```

## 4) `.gitignore`

Файл:
[`/.gitignore`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/.gitignore)

Что важно:

- исключаем `.env` и `*.env` (чтобы не хранить секреты в репозитории)
- игнорируем `migrations/versions/*.py` (кроме `migrations/versions/__init__.py`)

## 5) Команды запуска миграций (как в практике)

После изменения схемы в [`app/models.py`](https://github.com/egorr-gubanov/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/app/models.py):

```bash
alembic revision --autogenerate -m "full data model"
alembic upgrade head
```

## 6) Итог практики

Результат:

- в проекте настроены миграции Alembic
- метаданные берутся из SQLModel
- переменные окружения вынесены в `.env`
- проектная структура соответствует требованиям практики
- документация по проекту собирается через MkDocs (см. `docs/`).

