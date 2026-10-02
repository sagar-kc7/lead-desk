from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from app.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    seed()
    yield


app = FastAPI(title="Lead Desk API", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}
