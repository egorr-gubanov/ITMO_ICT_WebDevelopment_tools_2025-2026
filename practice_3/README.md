# Практика 3 (отдельная учебная реализация)

Это отдельный учебный пример под Практику 3: миграции Alembic, `.env`, `.gitignore` и структура проекта.

## Что сделано

- `practice_3/connection.py`:
  - загрузка `.env`
  - `DB_URL` через `os.getenv`
  - `engine`, `init_db`, `get_session`
- `practice_3/models.py`:
  - SQLModel-модели
  - many-to-many через `UserSkillLink`
  - добавлено поле `level` в связующей таблице
- `practice_3/alembic.ini`
- `practice_3/migrations/env.py`:
  - `target_metadata = SQLModel.metadata`
  - чтение `DB_URL` из `.env` (fallback на `alembic.ini`)
- `practice_3/migrations/script.py.mako`:
  - импорт `sqlmodel`
- `practice_3/migrations/versions/0001_add_level_to_userskilllink.py`:
  - пример миграции добавления поля `level`
- `practice_3/.gitignore`:
  - исключение `.env` и файлов окружения

## Как запускать миграции в practice_3

```bash
alembic -c practice_3/alembic.ini revision --autogenerate -m "skill link level added"
alembic -c practice_3/alembic.ini upgrade head
```

## Запуск учебного приложения

```bash
uvicorn practice_3.main:app --reload
```
