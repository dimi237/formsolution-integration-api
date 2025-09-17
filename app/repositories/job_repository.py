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
            "status": "RUNNING",
            "created_at": datetime.utcnow(),
            "executions": []      
        })
        result = await self.db.jobs.insert_one(job_dict)
        job_dict["_id"] = str(result.inserted_id)
        job_dict["created_at"] = job_dict["created_at"].isoformat() 
        return JobInDB(**job_dict)

    async def get_by_item_id(self, item_id: str) -> Optional[JobInDB]:
        doc = await self.db.jobs.find_one({"item_id": item_id})
        if "created_at" in doc:
                doc["created_at"] = doc["created_at"].isoformat() 
        doc["_id"] = str(doc["_id"])   
        
        return JobInDB(**doc) if doc else None

    async def update_status(self, item_id: str, status: str) -> Optional[any]:
        result = await self.db.jobs.find_one_and_update(
            {"item_id": item_id},
            {"$set": {"status": status}},
            return_document=True
        )
        return result if result else None

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
    async def get_running_jobs(self) -> list[JobInDB]:
        """
        Retourne la liste des jobs avec statut RUNNING.
        """
        cursor = self.db.jobs.find({"status": "RUNNING"})
        jobs: list[JobInDB] = []
        async for job in cursor:
           if "created_at" in job:
                job["created_at"] = job["created_at"].isoformat() 
           job["_id"] = str(job["_id"])   
           jobs.append(JobInDB(**job))
        return jobs
    
    async def exists(self, item_id: str) -> bool:
        job = await self.db.jobs.find_one({"item_id": item_id})
        return job is not None
    async def update_job(self, item_id: str, update: dict, array_filters: list = None):
        """
        Met à jour un job avec une requête MongoDB personnalisée.
        Exemple d'usage : 
            await repo.update_job(item_id, {"$set": {"status": "CLOSED"}})
        """
        query = {"item_id": item_id}
        try:
            result = await self.db.jobs.update_one(query, update, array_filters=array_filters)
            return result
        except Exception as exc:
            print(f"❌ Erreur update_job sur {item_id} : {exc}")
            raise
    async def get_job_stats(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await self.db.jobs.aggregate(pipeline).to_list(length=None)

        stats = {"total": 0, "RUNNING": 0, "PAUSED": 0, "FAILED": 0}

        for r in results:
            status = r["_id"]
            count = r["count"]
            stats["total"] += count
            if status in stats:
                stats[status] = count

        return stats
def get_repo():
    return JobRepository()
