import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
if os.getenv("LOAD_ENV_FILE", "true").lower() != "false":
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers.api import router
from .routers.connections import router as connections_router
from .routers.records import router as records_router
from .routers.planning import router as planning_router
from .routers.review import router as review_router
from .config import validate_configuration, production
from .security import RequestGuards
from .database import connect
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import sqlite3

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_configuration()
    init_db()
    yield

app = FastAPI(title="PaisaPilot AI API", version="0.3.0", description="Financial literacy workspace with published market data and optional account connections.", lifespan=lifespan, docs_url=None if production() else "/docs", redoc_url=None if production() else "/redoc", openapi_url=None if production() else "/openapi.json")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])
app.add_middleware(RequestGuards)
app.include_router(router)
app.include_router(connections_router)
app.include_router(records_router)
app.include_router(planning_router)
app.include_router(review_router)

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Never echo financial input, credentials, or non-finite JSON values.
    return JSONResponse(status_code=422, content={"detail": "Check the highlighted inputs and try again.", "errors": [{"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]} for error in exc.errors()]})

@app.get("/health")
def health():
    return {"status": "ok", "service": "paisa-pilot-api"}

@app.get("/ready")
def ready():
    try:
        with connect() as db:
            db.execute("SELECT 1 FROM app_meta LIMIT 1").fetchone()
    except sqlite3.Error:
        raise HTTPException(503, "Database is not ready.")
    return {"status": "ready"}
