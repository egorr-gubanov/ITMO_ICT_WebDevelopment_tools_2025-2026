# Лабораторная работа 2. Потоки. Процессы. Асинхронность.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск программ

### Задача 1: Вычисление суммы

```bash
cd task_1/threading_solution
python main.py
```

```bash
cd task_1/multiprocessing_solution
python main.py
```

```bash
cd task_1/async_solution
python main.py
```

### Задача 2: Парсинг веб-страниц

```bash
cd task_2/threading_solution
python main.py
```

```bash
cd task_2/multiprocessing_solution
python main.py
```

```bash
cd task_2/async_solution
python main.py
```

## Документация

Для просмотра документации MkDocs:

```bash
mkdocs serve
```

После этого откройте браузер по адресу http://127.0.0.1:8000

Для сборки статической документации:

```bash
mkdocs build
```

## Структура проекта

```
├── mkdocs.yml
├── requirements.txt
├── README.md
├── task_1/
│   ├── threading_solution/main.py
│   ├── multiprocessing_solution/main.py
│   └── async_solution/main.py
├── task_2/
│   ├── threading_solution/main.py
│   ├── multiprocessing_solution/main.py
│   └── async_solution/main.py
└── docs/
    ├── index.md
    ├── task_1.md
    ├── task_2.md
    ├── comparison.md
    └── conclusion.md
```
