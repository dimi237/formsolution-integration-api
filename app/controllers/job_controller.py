from fastapi import HTTPException, Depends
from app.core.scheduler import get_scheduler
from app.models.job_model import JobCreate, JobInDB
from app.services.job_service import JobService
from typing import List
from fastapi import status

class JobController:
        
    def get_job_service() -> JobService:
        return JobService(get_scheduler())

    # Endpoint POST /jobs/
    async def create_job(self, job_data: JobCreate, service: JobService = Depends(get_job_service)):
        try:
            job = await service.create_job(job_data=job_data)
            return job
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    # Endpoint GET /jobs/
    async def list_jobs(self, service: JobService = Depends(get_job_service)) -> List[JobInDB]:
        jobs = await service.list_jobs()
        return  [j.dict() for j in jobs] 

    # Endpoint PATCH /jobs/{item_id}/pause
    async def pause_job(self, item_id: str, service: JobService = Depends(get_job_service)):
        try:
            await service.pause_job(item_id)
            return {"message": f"Job {item_id} paused"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    # Endpoint PATCH /jobs/{item_id}/resume
    async def resume_job(self, item_id: str, service: JobService = Depends(get_job_service)):
        try:
            await service.resume_job(item_id)
            return {"message": f"Job {item_id} resumed"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    # Endpoint DELETE /jobs/{item_id}
    async def delete_job(self, item_id: str, service: JobService = Depends(get_job_service)):
        try:
            await service.delete_job(item_id)
            return {"message": f"Job {item_id} deleted"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

