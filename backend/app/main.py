from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.leads import router as leads_router
from app.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    seed()
    yield


app = FastAPI(title="Lead Desk API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(admin_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = first["loc"][-1] if first["loc"] else "input"
    return JSONResponse(
        status_code=422,
        content={"error": f"Invalid {field}: {first['msg']}"},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
