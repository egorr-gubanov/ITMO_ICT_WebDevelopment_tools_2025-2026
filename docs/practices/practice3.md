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

В основной структуре проекта используется корневая папка миграций:

- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/versions/1a2b3c4d5e6f_initial_schema.py`

Базовая миграция `1a2b3c4d5e6f_initial_schema.py` создаёт актуальную схему:

- таблицы `user`, `skill`, `project`, `team`;
- ассоциативные таблицы `userskilllink`, `teammember`;
- enum `roletype` со значениями ролей.

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
- не игнорируем файлы миграций в `migrations/versions`, чтобы они хранились в git

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

## Отдельный блок: простая учебная реализация Практики 3

Дополнительно в проекте есть отдельная учебная версия Практики 3 (чтобы не смешивать с основной боевой структурой):

- `practice_3/main.py`
- `practice_3/connection.py`
- `practice_3/models.py`
- `practice_3/alembic.ini`
- `practice_3/migrations/env.py`
- `practice_3/migrations/script.py.mako`
- `practice_3/migrations/versions/0001_add_level_to_userskilllink.py`
- `practice_3/.gitignore`
- `practice_3/.env.example`

Что демонстрирует этот блок:

- настройку Alembic для SQLModel (`target_metadata = SQLModel.metadata`);
- загрузку URL базы из `.env` в `connection.py` и `migrations/env.py`;
- передачу URL в Alembic через окружение (fallback на `alembic.ini`);
- пример миграции с изменением схемы (`level` в `userskilllink`);
- корректный локальный `.gitignore` для исключения `.env`.

