from fastapi import FastAPI
from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

from app.core.scheduler import init_scheduler
from app.middlewares.auth_middleware import AuthMiddleware
from app.scripts.restore import restore_running_jobs
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    init_scheduler()
    await restore_running_jobs() 
    yield
    # Shutdown
    await close_mongo_connection()
    
def create_app() -> FastAPI:
    """Factory pour créer l'application FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AuthMiddleware)
    from app.api.v1.job import router as job_router
    from app.api.v1.dossier import router as dossier_router
    from app.api.v1.stats import router as stat_router
    from app.api.v1.auth import router as auth_router
    app.include_router(
        job_router,
        prefix="/api/v1/jobs",
        tags=["Jobs"]
)
    app.include_router(
        dossier_router,
        prefix="/api/v1/dossiers",
        tags=["dossiers"]
)
    app.include_router(
        stat_router,
        prefix="/api/v1/stats",
        tags=["stats"]
)
    app.include_router(
        auth_router,
        prefix="/api/v1/auth",
        tags=["auth"]
)

    return app


app = create_app()
