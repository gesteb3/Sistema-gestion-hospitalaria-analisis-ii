from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.init_db import initialize_database
from app.db.session import engine


settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        "Iniciando %s versión %s en ambiente %s",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )

    initialize_database()
    logger.info("Tablas y datos iniciales verificados correctamente.")

    yield

    engine.dispose()
    logger.info("Conexiones de base de datos cerradas correctamente.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST para administrar los procesos clínicos y administrativos "
        "del Sistema de Gestión Hospitalaria."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    return {
        "sistema": settings.app_name,
        "version": settings.app_version,
        "estado": "API funcionando",
        "swagger": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
