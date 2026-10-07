import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from asyncpg import PostgresError
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import create_database_engine
from config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_database_engine(get_settings())
    app.state.database_engine = engine
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="post-rely", lifespan=lifespan)
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent / "templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="creator/home.html",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> JSONResponse:
    engine = request.app.state.database_engine
    try:
        async with asyncio.timeout(3):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, PostgresError, OSError, TimeoutError):
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(content={"status": "ready"})
