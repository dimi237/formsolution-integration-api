from app.repositories.job_repository import JobRepository
from app.core.scheduler import get_scheduler
from app.scripts.download_documents import process_item_cron

async def restore_running_jobs():
    """
    Recharge tous les jobs avec statut RUNNING depuis la base
    et les programme dans le scheduler.
    """
    repo = JobRepository()
    jobs = await repo.get_running_jobs()
    scheduler = get_scheduler()

    for job in jobs:
        try:
            scheduler.add_job(
                job_id=job.item_id,
                func=process_item_cron,
                args=[job.item_id],
                trigger="interval",
                seconds=job.frequency
            )
            print(f"✅ Job {job.item_id} restauré dans le scheduler.")
        except Exception as e:
            print(f"⚠️ Impossible de restaurer {job.item_id} : {e}")
