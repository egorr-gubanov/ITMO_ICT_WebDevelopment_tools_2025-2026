import sqlite3
import threading
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def create_database():
    conn = sqlite3.connect("lab1_database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'developer',
            bio TEXT NOT NULL DEFAULT '',
            hashed_password TEXT NOT NULL DEFAULT ''
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    
    cursor.execute("""
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES project(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS userskilllink (
            user_id INTEGER,
            skill_id INTEGER,
            proficiency_level TEXT NOT NULL DEFAULT 'beginner',
            PRIMARY KEY (user_id, skill_id),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (skill_id) REFERENCES skill(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teammember (
            user_id INTEGER,
            team_id INTEGER,
            member_role TEXT NOT NULL DEFAULT 'member',
            PRIMARY KEY (user_id, team_id),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (team_id) REFERENCES team(id)
        )
    """)
    
    conn.commit()
    conn.close()


def parse_and_save(url, skill_name, lock):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "Unknown"
        
        conn = sqlite3.connect("lab1_database.db")
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO user (username, email, role, bio) VALUES (?, ?, ?, ?)",
            (title[:50], url.split("//")[1].split("/")[0], "developer", f"Parsed from {url}")
        )
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO skill (name, description) VALUES (?, ?)",
            (skill_name, f"Skill for {url}")
        )
        skill_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO project (title, description, status, owner_id) VALUES (?, ?, ?, ?)",
            (f"Project for {skill_name}", f"Auto-created from {url}", "open", user_id)
        )
        project_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO team (name, description, project_id) VALUES (?, ?, ?)",
            (f"Team {skill_name}", f"Team for {skill_name} project", project_id)
        )
        team_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO userskilllink (user_id, skill_id, proficiency_level) VALUES (?, ?, ?)",
            (user_id, skill_id, "intermediate")
        )
        
        cursor.execute(
            "INSERT INTO teammember (user_id, team_id, member_role) VALUES (?, ?, ?)",
            (user_id, team_id, "lead")
        )
        
        conn.commit()
        conn.close()
        
        print(f"URL: {url}")
        print(f"User: {title[:50]}")
        print(f"Skill: {skill_name}")
        print(f"Project and Team created")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return False


def worker(args):
    url, skill_name, lock = args
    return parse_and_save(url, skill_name, lock)


def main():
    urls_and_skills = [
        ("https://www.python.org", "Python"),
        ("https://docs.python.org/3/", "Python"),
        ("https://www.djangoproject.com/", "Django"),
        ("https://flask.palletsprojects.com/", "Flask"),
        ("https://fastapi.tiangolo.com/", "FastAPI"),
        ("https://pypi.org/", "PyPI"),
        ("https://www.sqlite.org/", "SQLite"),
        ("https://example.com", "Web"),
    ]

    create_database()
    
    lock = threading.Lock()
    start_time = time.perf_counter()
    
    threads = []
    for url, skill_name in urls_and_skills:
        thread = threading.Thread(target=worker, args=((url, skill_name, lock),))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
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
    main()
