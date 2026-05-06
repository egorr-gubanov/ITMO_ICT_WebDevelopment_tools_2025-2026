import asyncio
import sqlite3
import time
from datetime import datetime

import aiohttp
import aiosqlite
from bs4 import BeautifulSoup


async def create_database():
    async with aiosqlite.connect("task_2_pages.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def parse_and_save(url, session):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "No title"

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        async with aiosqlite.connect("task_2_pages.db") as db:
            await db.execute(
                "INSERT INTO pages (url, title, created_at) VALUES (?, ?, ?)",
                (url, title, created_at)
            )
            await db.commit()

        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Saved at: {created_at}")
        print("-" * 50)
        return title
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        try:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect("task_2_pages.db") as db:
                await db.execute(
                    "INSERT INTO pages (url, title, created_at) VALUES (?, ?, ?)",
                    (url, "error", created_at)
                )
                await db.commit()
        except:
            pass
        return "error"


async def main():
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

    await create_database()

    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()

    print(f"\nВсего обработано URL: {len(urls)}")
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
