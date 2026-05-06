# Задача 2 (из лабораторной работы 1). Заполнение БД платформы поиска команды

## Описание задачи

В лабораторной работе 1 была создана база данных для платформы поиска людей в команду. Эта база данных содержит таблицы:

- **user** - пользователи с ролями (developer, designer, manager, marketer, junior, tester, devops)
- **skill** - навыки пользователей
- **project** - проекты
- **team** - команды
- **userskilllink** - связь многие-ко-многим между пользователями и навыками
- **teammember** - связь многие-ко-многим между пользователями и командами

Задача состоит в том, чтобы заполнить эту базу данных данными, полученными путём парсинга профилей GitHub - реальной платформы для поиска разработчиков.

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

Программы парсят профили GitHub известных разработчиков и организаций:

| GitHub профиль | Навык | Кто |
|----------------|-------|-----|
| https://github.com/gaearon | React | Dan Abramov (создатель Redux) |
| https://github.com/sindresorhus | Node.js | Sindre Sorhus (1000+ npm пакетов) |
| https://github.com/torvalds | Linux | Linus Torvalds (создатель Linux) |
| https://github.com/yyx990803 | Vue.js | Evan You (создатель Vue.js) |
| https://github.com/mitsuhiko | Flask | Armin Ronacher (создатель Flask) |
| https://github.com/kennethreitz | Python | Kenneth Reitz (создатель requests) |
| https://github.com/jakevdp | Data Science | Jake VanderPlas (Python Data Science) |
| https://github.com/tiangolo | FastAPI | Sebastián Ramírez (создатель FastAPI) |
| https://github.com/pallets | Django | Pallets Projects (Flask, Click) |
| https://github.com/psf | Python | Python Software Foundation |
| https://github.com/microsoft | TypeScript | Microsoft (TypeScript, VS Code) |
| https://github.com/facebook | React | Facebook (React, React Native) |

## Что парсится

Для каждого профиля GitHub извлекаются:

1. **username** - имя пользователя
2. **bio** - описание профиля (становится bio пользователя)
3. **Количество репозиториев** - сохраняется в описание проекта

## Реализация threading

Для каждого профиля создаётся отдельный поток. Каждый поток:
1. Загружает HTML-страницу профиля GitHub
2. Извлекает username, bio, количество репозиториев
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
| Threading | ~5-10 секунд |
| Multiprocessing | ~5-10 секунд |
| Async | ~3-5 секунд |

## Результат заполнения БД

После выполнения программы база данных содержит:

- 12 пользователей (реальные разработчики)
- 12 навыков
- 12 проектов
- 12 команд
- 12 связей пользователь-навык
- 12 членов команд

## Почему GitHub

GitHub - идеальный источник данных для платформы поиска команды:

1. **Открытые профили** - не требуют авторизации
2. **Реальные разработчики** - актуальные данные
3. **Навыки видны** - по репозиториям и организациям
4. **Легальный парсинг** - публичные данные

## Вывод

Данная задача демонстрирует применение параллельного программирования для заполнения реальной базы данных реальными данными с GitHub. Async показывает лучшие результаты благодаря эффективной обработке сетевых запросов.
