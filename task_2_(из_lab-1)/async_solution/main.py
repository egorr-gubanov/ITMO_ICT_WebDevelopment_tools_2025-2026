import asyncio
import sqlite3
import time

import aiohttp
import aiosqlite
from bs4 import BeautifulSoup


async def create_database():
    async with aiosqlite.connect("lab1_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'developer',
                bio TEXT NOT NULL DEFAULT '',
                hashed_password TEXT NOT NULL DEFAULT ''
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS skill (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'open',
                owner_id INTEGER,
                FOREIGN KEY (owner_id) REFERENCES user(id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS team (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES project(id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS userskilllink (
                user_id INTEGER,
                skill_id INTEGER,
                proficiency_level TEXT NOT NULL DEFAULT 'beginner',
                PRIMARY KEY (user_id, skill_id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (skill_id) REFERENCES skill(id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS teammember (
                user_id INTEGER,
                team_id INTEGER,
                member_role TEXT NOT NULL DEFAULT 'member',
                PRIMARY KEY (user_id, team_id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (team_id) REFERENCES team(id)
            )
        """)
        
        await db.commit()


async def parse_and_save(url, skill_name, session):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
        
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "Unknown"
        
        async with aiosqlite.connect("lab1_database.db") as db:
            await db.execute(
                "INSERT INTO user (username, email, role, bio) VALUES (?, ?, ?, ?)",
                (title[:50], url.split("//")[1].split("/")[0], "developer", f"Parsed from {url}")
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            user_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO skill (name, description) VALUES (?, ?)",
                (skill_name, f"Skill for {url}")
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            skill_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO project (title, description, status, owner_id) VALUES (?, ?, ?, ?)",
                (f"Project for {skill_name}", f"Auto-created from {url}", "open", user_id)
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            project_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO team (name, description, project_id) VALUES (?, ?, ?)",
                (f"Team {skill_name}", f"Team for {skill_name} project", project_id)
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            team_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO userskilllink (user_id, skill_id, proficiency_level) VALUES (?, ?, ?)",
                (user_id, skill_id, "intermediate")
            )
            
            await db.execute(
                "INSERT INTO teammember (user_id, team_id, member_role) VALUES (?, ?, ?)",
                (user_id, team_id, "lead")
            )
            
            await db.commit()
        
        print(f"URL: {url}")
        print(f"User: {title[:50]}")
        print(f"Skill: {skill_name}")
        print(f"Project and Team created")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return False


async def main():
    urls_and_skills = [
        ("https://www.python.org", "Python"),
        ("https://www.djangoproject.com/", "Django"),
        ("https://fastapi.tiangolo.com/", "FastAPI"),
        ("https://react.dev/", "React"),
        ("https://angular.dev/", "Angular"),
        ("https://vuejs.org/", "Vue.js"),
        ("https://nodejs.org/", "Node.js"),
        ("https://www.postgresql.org/", "PostgreSQL"),
        ("https://www.docker.com/", "Docker"),
        ("https://kubernetes.io/", "Kubernetes"),
        ("https://www.figma.com/", "Figma"),
        ("https://www.selenium.dev/", "Selenium"),
    ]

    await create_database()
    
    start_time = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(url, skill_name, session) for url, skill_name in urls_and_skills]
        results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    
    conn = sqlite3.connect("lab1_database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM user")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM skill")
    skill_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM project")
    project_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM team")
    team_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM userskilllink")
    link_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM teammember")
    member_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\nСтатистика базы данных:")
    print(f"Пользователей: {user_count}")
    print(f"Навыков: {skill_count}")
    print(f"Проектов: {project_count}")
    print(f"Команд: {team_count}")
    print(f"Связей пользователь-навык: {link_count}")
    print(f"Членов команд: {member_count}")
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
