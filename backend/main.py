import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database.connection import create_database_tables
from middleware.errors import register_exception_handlers
from middleware.rate_limit import InMemoryRateLimitMiddleware
from routes.api import router as api_router
from routes.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("beingai.api")

settings = get_settings()

app = FastAPI(
    title="BeingAI Assistant API",
    version="0.1.0",
    description="Automation orchestration API for BeingAI Assistant.",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app, settings)

app.add_middleware(InMemoryRateLimitMiddleware)

app.include_router(health_router)
app.include_router(api_router)

@app.on_event("startup")
async def log_startup_configuration() -> None:
    create_database_tables()
    for issue in settings.production_issues():
        logger.warning("Production configuration: %s", issue)
