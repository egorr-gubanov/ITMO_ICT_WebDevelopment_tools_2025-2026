# Практика 1 (ваш проект, отдельная папка)

Эта папка реализует требования Практики 1 на домене платформы поиска людей в команду, не затрагивая основной код в `app/`.

## Что реализовано

- Отдельное FastAPI-приложение в `practice_1/main.py`
- Временная БД (2+ записи) для главной сущности `User`
- У главной сущности есть:
  - одиночный вложенный объект `project`
  - список вложенных объектов `skills`
- Pydantic-модели в `practice_1/models.py`
- CRUD-эндпоинты:
  - для `users` (главная таблица)
  - для `projects` (вложенный объект)
  - для `skills` (список вложенных объектов)
- Аннотации типов и `TypedDict`-ответы для POST

## Эндпоинты

- `GET /`
- `GET /users`
- `GET /user/{user_id}`
- `POST /user`
- `PUT /user/{user_id}`
- `DELETE /user/delete/{user_id}`

- `GET /projects`
- `GET /project/{project_id}`
- `POST /project`
- `PUT /project/{project_id}`
- `DELETE /project/delete/{project_id}`

- `GET /skills`
- `GET /skill/{skill_id}`
- `POST /skill`
- `PUT /skill/{skill_id}`
- `DELETE /skill/delete/{skill_id}`

## Запуск

Из корня проекта:

```bash
uvicorn practice_1.main:app --reload
```

Проверка:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
