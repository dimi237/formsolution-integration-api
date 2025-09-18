from fastapi import APIRouter
from typing import List
from app.controllers.job_controller import JobController
from app.models.job_model import JobInDB

router = APIRouter()

controller = JobController()

router.post("/", response_model=JobInDB)(controller.create_job)
router.put("/{id}")(controller.update_job)
router.get("/", response_model=List[JobInDB])(controller.list_jobs)
router.patch("/{item_id}/pause")(controller.pause_job)
router.patch("/{item_id}/resume")(controller.resume_job)
router.delete("/{item_id}")(controller.delete_job)
router.get("/stats/")(controller.get_job_stats)
router.get("/{item_id}/detail")(controller.get_job)

            