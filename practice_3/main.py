from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from practice_3.connection import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "Practice 3: migrations, env and gitignore"
