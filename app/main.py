from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from app.connection import init_db
from app.routers import auth, me, projects, skills, teams, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(teams.router)
app.include_router(auth.router)
app.include_router(me.router)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "Платформа поиска людей в команду"
