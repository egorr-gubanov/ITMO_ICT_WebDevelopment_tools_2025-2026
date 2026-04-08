# Практика 2 (отдельная учебная реализация)

Это отдельная реализация Практики 2 для вашего проекта (платформа поиска людей в команду), без изменений основного приложения в `app/`.

## Что есть в практике

- Подключение к PostgreSQL через SQLModel в `practice_2/connection.py`
- Таблицы и связи в `practice_2/models.py`:
  - `User`, `Skill`, `Project`
  - `UserSkillLink` (many-to-many с `proficiency_level`)
- CRUD-эндпоинты в `practice_2/main.py`
- Вложенное отображение связей:
  - `GET /user/{user_id}` с `response_model=UserWithRelations`

## Запуск

1. Убедитесь, что PostgreSQL доступен и переменная `DB_URL` настроена (или используется значение по умолчанию).
2. Запуск:

```bash
uvicorn practice_2.main:app --reload
```

Проверка:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
