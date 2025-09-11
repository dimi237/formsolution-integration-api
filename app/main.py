from fastapi import FastAPI
from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

from app.core.scheduler import init_scheduler
from app.scripts.restore import restore_running_jobs

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
        
    from app.api.v1.job import router as job_router
    app.include_router(
        job_router,
        prefix="/api/v1/jobs",
        tags=["Jobs"]
)

    return app


app = create_app()
