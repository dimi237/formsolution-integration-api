from typing import List, Optional
from datetime import datetime
from app.core.db import get_db
from app.models.job_model import JobInDB, JobCreate

class JobRepository:
    def __init__(self):
        self.db = get_db()

    async def create(self, job: JobCreate) -> JobInDB:
        job_dict = job.dict()
        job_dict.update({
            "status": "running",
            "created_at": datetime.utcnow()
        })
        result = await self.db.jobs.insert_one(job_dict)
        job_dict["_id"] = str(result.inserted_id)
        job_dict["created_at"] = job_dict["created_at"].isoformat() 
        return JobInDB(**job_dict)

    async def get_by_item_id(self, item_id: str) -> Optional[JobInDB]:
        doc = await self.db.jobs.find_one({"item_id": item_id})
        return JobInDB(**doc) if doc else None

    async def update_status(self, item_id: str, status: str) -> Optional[JobInDB]:
        result = await self.db.jobs.find_one_and_update(
            {"item_id": item_id},
            {"$set": {"status": status}},
            return_document=True
        )
        return JobInDB(**result) if result else None

    async def delete(self, item_id: str) -> bool:
        result = await self.db.jobs.delete_one({"item_id": item_id})
        return result.deleted_count > 0
    
    async def get_all(self) -> List[JobInDB]:
        """Renvoie tous les jobs"""
        jobs = []
        
        async for doc in self.db.jobs.find({}):
            if "created_at" in doc:
                doc["created_at"] = doc["created_at"].isoformat() 
            doc["_id"] = str(doc["_id"])   
            jobs.append(JobInDB(**doc))
        return jobs