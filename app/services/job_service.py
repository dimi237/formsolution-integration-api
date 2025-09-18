from typing import Optional, List
from fastapi import Depends
from app.repositories.job_repository import JobRepository
from app.core.scheduler import Scheduler, get_scheduler
from app.models.job_model import JobCreate, JobInDB
import logging

from app.scripts.fetch_files import process_files

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, scheduler: Scheduler = Depends(get_scheduler)):
        self.repo = JobRepository()
        self.scheduler = scheduler

    async def create_job(self, job_data: JobCreate) -> JobInDB:
        """
        Crée le job en DB et le planifie dans le scheduler
        """
        if await self.repo.exists(job_data.item_id):
            raise ValueError(f"Job avec item_id {job_data.item_id} existe déjà.")
        # 1️⃣ Sauvegarder en DB
        saved_job = await self.repo.create(job_data)

        # 2️⃣ Ajouter le job au scheduler
        self.scheduler.add_job(
            job_id=saved_job.item_id,
            func=process_files,
            args=[saved_job.item_id],
            trigger="interval",
            seconds=saved_job.frequency  # fréquence en secondes
        )
        logger.info(f"Job {saved_job.item_id} planifié")
        return saved_job
    async def update_job(self, job_data: JobCreate, id:str) -> JobInDB:
        saved_job = await self.repo.update_jobf(id, {"$set": job_data.dict()})
        job = self.scheduler.get_job(job_data.item_id)
        if job:
            self.scheduler.reschedule_job(
            job_id=job_data.item_id,
            trigger="interval",
            seconds=job_data.frequency 
        )
        
        return saved_job

    async def pause_job(self, item_id: str) -> Optional[JobInDB]:
        """Met le job en pause"""
        self.scheduler.pause_job(item_id)
        return await self.repo.update_status(item_id, "PAUSED")

    async def resume_job(self, item_id: str) -> Optional[JobInDB]:
        """Relance le job"""
        if self.scheduler.get_job(item_id):
           self.scheduler.resume_job(item_id)
        else:
            job = await self.repo.get_by_item_id(item_id)
            self.scheduler.add_job(
            job_id=job.item_id,
            func=process_files,
            args=[job.item_id],
            trigger="interval",
            seconds=job.frequency
        )
        return await self.repo.update_status(item_id, "RUNNING")

    async def delete_job(self, item_id: str) -> Optional[JobInDB]:
        """Supprime le job du scheduler et de la DB"""
        self.scheduler.remove_job(item_id)
        return await self.repo.delete(item_id)

    async def list_jobs(self) -> List[JobInDB]:
        """Liste tous les jobs en DB"""
        return await self.repo.get_all()
    async def get_job_stats(self):
        return await self.repo.get_job_stats()
    async def get_job_by_item_id(self,item_id: str ):
        return await self.repo.get_by_item_id(item_id)
