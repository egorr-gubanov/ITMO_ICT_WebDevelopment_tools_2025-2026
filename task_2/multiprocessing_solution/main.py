import sqlite3
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def create_database():
    conn = sqlite3.connect("task_2_pages.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def parse_and_save(url):
    try:
        conn = sqlite3.connect("task_2_pages.db")
        cursor = conn.cursor()

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "No title"

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO pages (url, title, created_at) VALUES (?, ?, ?)",
            (url, title, created_at)
        )
        conn.commit()
        conn.close()

        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Saved at: {created_at}")
        print("-" * 50)
        return title
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        try:
            conn = sqlite3.connect("task_2_pages.db")
            cursor = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO pages (url, title, created_at) VALUES (?, ?, ?)",
                (url, "error", created_at)
            )
            conn.commit()
            conn.close()
        except:
            pass
        return "error"


def main():
    import multiprocessing

    urls = [
        "https://example.com",
        "https://www.python.org",
        "https://docs.python.org/3/",
        "https://www.djangoproject.com/",
        "https://flask.palletsprojects.com/",
        "https://fastapi.tiangolo.com/",
        "https://pypi.org/",
        "https://www.sqlite.org/",
    ]

    create_database()

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=len(urls)) as pool:
        results = pool.map(parse_and_save, urls)

    end_time = time.perf_counter()

    print(f"\nВсего обработано URL: {len(urls)}")
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    main()
