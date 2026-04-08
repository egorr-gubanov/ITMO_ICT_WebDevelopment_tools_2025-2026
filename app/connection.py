import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

db_url = os.getenv("DB_URL", "postgresql://postgres:123@localhost/teamfinder_db")
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
