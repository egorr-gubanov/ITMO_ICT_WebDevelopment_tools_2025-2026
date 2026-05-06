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


async def parse_github_profile(github_url, skill_name, session):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        async with session.get(github_url, headers=headers, timeout=15) as response:
            response.raise_for_status()
            html = await response.text()
        
        soup = BeautifulSoup(html, "html.parser")
        
        username_elem = soup.find("span", class_="p-nickname")
        username = username_elem.text.strip() if username_elem else github_url.split("/")[-1]
        
        bio_elem = soup.find("div", class_="p-note")
        bio = bio_elem.text.strip()[:200] if bio_elem else ""
        
        repo_elem = soup.find("span", class_="Counter")
        repo_count = repo_elem.text.strip() if repo_elem else "0"
        
        async with aiosqlite.connect("lab1_database.db") as db:
            await db.execute(
                "INSERT INTO user (username, email, role, bio) VALUES (?, ?, ?, ?)",
                (username, f"{username}@github.com", "developer", bio)
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            user_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO skill (name, description) VALUES (?, ?)",
                (skill_name, f"Skill from GitHub profile: {github_url}")
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            skill_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO project (title, description, status, owner_id) VALUES (?, ?, ?, ?)",
                (f"Project by {username}", f"Repos: {repo_count}", "open", user_id)
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            project_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO team (name, description, project_id) VALUES (?, ?, ?)",
                (f"Team {username}", f"Team led by {username}", project_id)
            )
            await db.commit()
            
            cursor = await db.execute("SELECT last_insert_rowid()")
            team_id = (await cursor.fetchone())[0]
            
            await db.execute(
                "INSERT INTO userskilllink (user_id, skill_id, proficiency_level) VALUES (?, ?, ?)",
                (user_id, skill_id, "expert")
            )
            
            await db.execute(
                "INSERT INTO teammember (user_id, team_id, member_role) VALUES (?, ?, ?)",
                (user_id, team_id, "lead")
            )
            
            await db.commit()
        
        print(f"GitHub: {github_url}")
        print(f"Username: {username}")
        print(f"Bio: {bio[:100]}..." if len(bio) > 100 else f"Bio: {bio}")
        print(f"Skill: {skill_name}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error parsing {github_url}: {e}")
        return False


async def main():
    github_profiles = [
        ("https://github.com/gaearon", "React"),
        ("https://github.com/sindresorhus", "Node.js"),
        ("https://github.com/torvalds", "Linux"),
        ("https://github.com/yyx990803", "Vue.js"),
        ("https://github.com/mitsuhiko", "Flask"),
        ("https://github.com/kennethreitz", "Python"),
        ("https://github.com/jakevdp", "Data Science"),
        ("https://github.com/tiangolo", "FastAPI"),
        ("https://github.com/pallets", "Django"),
        ("https://github.com/psf", "Python"),
        ("https://github.com/microsoft", "TypeScript"),
        ("https://github.com/facebook", "React"),
    ]

    await create_database()
    
    start_time = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        tasks = [parse_github_profile(url, skill, session) for url, skill in github_profiles]
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
