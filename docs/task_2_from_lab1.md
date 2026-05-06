# Задача 2 (из лабораторной работы 1). Заполнение БД платформы поиска команды

## Описание задачи

В лабораторной работе 1 была создана база данных для платформы поиска людей в команду. Эта база данных содержит таблицы:

- **user** - пользователи с ролями (developer, designer, manager, marketer, junior, tester, devops)
- **skill** - навыки пользователей
- **project** - проекты
- **team** - команды
- **userskilllink** - связь многие-ко-многим между пользователями и навыками
- **teammember** - связь многие-ко-многим между пользователями и командами

Задача состоит в том, чтобы заполнить эту базу данных данными, полученными путём парсинга веб-страниц.

## Структура базы данных

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'developer',
    bio TEXT NOT NULL DEFAULT '',
    hashed_password TEXT NOT NULL DEFAULT ''
);

CREATE TABLE skill (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open',
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES user(id)
);

CREATE TABLE team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    project_id INTEGER,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

CREATE TABLE userskilllink (
    user_id INTEGER,
    skill_id INTEGER,
    proficiency_level TEXT NOT NULL DEFAULT 'beginner',
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (skill_id) REFERENCES skill(id)
);

CREATE TABLE teammember (
    user_id INTEGER,
    team_id INTEGER,
    member_role TEXT NOT NULL DEFAULT 'member',
    PRIMARY KEY (user_id, team_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);
```

## Источники данных

Программы парсят следующие веб-сайты и создают соответствующие записи:

| URL | Навык |
|-----|-------|
| https://www.python.org | Python |
| https://docs.python.org/3/ | Python |
| https://www.djangoproject.com/ | Django |
| https://flask.palletsprojects.com/ | Flask |
| https://fastapi.tiangolo.com/ | FastAPI |
| https://pypi.org/ | PyPI |
| https://www.sqlite.org/ | SQLite |
| https://example.com | Web |

## Реализация threading

Для каждого URL создаётся отдельный поток. Каждый поток:
1. Загружает HTML-страницу
2. Извлекает заголовок страницы (тег `<title>`)
3. Создаёт записи в таблицах: user, skill, project, team, userskilllink, teammember

Код находится в файле `task_2_(из_lab-1)/threading_solution/main.py`.

## Реализация multiprocessing

Используется `multiprocessing.Pool` для распределения задач по процессам. Каждый процесс создаёт собственное подключение к SQLite.

Код находится в файле `task_2_(из_lab-1)/multiprocessing_solution/main.py`.

## Реализация async

Используются асинхронные библиотеки `aiohttp` для HTTP-запросов и `aiosqlite` для работы с SQLite.

Код находится в файле `task_2_(из_lab-1)/async_solution/main.py`.

## Результаты времени выполнения

| Подход | Время выполнения |
|--------|------------------|
| Threading | ~1-2 секунд |
| Multiprocessing | ~1-2 секунд |
| Async | ~1-2 секунд |

## Результат заполнения БД

После выполнения программы база данных содержит:

- 8 пользователей
- 8 навыков
- 8 проектов
- 8 команд
- 8 связей пользователь-навык
- 8 членов команд

## Вывод

Данная задача демонстрирует применение параллельного программирования для заполнения реальной базы данных, созданной в лабораторной работе 1. Все три подхода успешно справляются с задачей, показывая похожие результаты по времени.
