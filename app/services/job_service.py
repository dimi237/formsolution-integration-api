from typing import Optional, List

from fastapi import Depends
from app.repositories.job_repository import JobRepository
from app.core.scheduler import Scheduler, get_scheduler
from app.models.job_model import JobCreate, JobInDB
import logging

from app.scripts.download_documents import process_item_cron

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, scheduler: Scheduler = Depends(get_scheduler)):
        self.repo = JobRepository()
        self.scheduler = scheduler

    async def create_job(self, job_data: JobCreate) -> JobInDB:
        """
        Crée le job en DB et le planifie dans le scheduler
        """
        # 1️⃣ Sauvegarder en DB
        saved_job = await self.repo.create(job_data)

        # 2️⃣ Ajouter le job au scheduler
        self.scheduler.add_job(
            job_id=saved_job.item_id,
            func=process_item_cron,
            args=[saved_job.item_id, saved_job.folder_id],
            trigger="interval",
            seconds=saved_job.frequency  # fréquence en secondes
        )
        logger.info(f"Job {saved_job.item_id} planifié")
        return saved_job

    async def pause_job(self, item_id: str) -> Optional[JobInDB]:
        """Met le job en pause"""
        self.scheduler.pause_job(item_id)
        return await self.repo.update_status(item_id, "paused")

    async def resume_job(self, item_id: str) -> Optional[JobInDB]:
        """Relance le job"""
        self.scheduler.resume_job(item_id)
        return await self.repo.update_status(item_id, "running")

    async def delete_job(self, item_id: str) -> Optional[JobInDB]:
        """Supprime le job du scheduler et de la DB"""
        self.scheduler.remove_job(item_id)
        return await self.repo.delete(item_id)

    async def list_jobs(self) -> List[JobInDB]:
        """Liste tous les jobs en DB"""
        return await self.repo.get_all()
