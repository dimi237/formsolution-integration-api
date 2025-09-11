from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        """Initialise le scheduler global."""
        self.scheduler = AsyncIOScheduler()
        print("⏰ Scheduler initialisé")
        
    def start(self):
        self.scheduler.start()
        print("⏰ Scheduler démarré")

    def add_job(self, job_id: str, func: str, args: list = None, trigger: str = "interval", **trigger_args):
        """Ajoute un job"""
        if not self.scheduler.get_job(job_id):
            self.scheduler.add_job(func, trigger=trigger, args=args, id=job_id, **trigger_args)
            logger.info(f"Job {job_id} ajouté au scheduler")
        else:
            logger.warning(f"Job {job_id} existe déjà dans le scheduler")

    def remove_job(self, job_id: str):
        """Supprime un job"""
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} supprimé du scheduler")

    def pause_job(self, job_id: str):
        """Met en pause un job"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.pause()
            logger.info(f"Job {job_id} mis en pause")

    def resume_job(self, job_id: str):
        """Relance un job"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.resume()
            logger.info(f"Job {job_id} relancé")
            
    def get_job(self, job_id: str):
        return self.scheduler.get_job(job_id)
    

# provider
_scheduler_instance: Scheduler | None = None

def get_scheduler() -> Scheduler:
    if _scheduler_instance is None:
        raise RuntimeError("Scheduler not initialized")
    return _scheduler_instance

def init_scheduler() -> Scheduler:
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = Scheduler()
        _scheduler_instance.start()  # <-- pas d'await
    return _scheduler_instance