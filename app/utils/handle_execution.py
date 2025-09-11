# app/utils/execution_handler.py
from datetime import datetime
from app.core.scheduler import get_scheduler
from app.repositories.job_repository import JobRepository

repo = JobRepository()


async def start_execution(item_id: str):
    """
    Démarre une nouvelle exécution : 
    - termine celle en cours (current=false, finishedAt=now)
    - ajoute une nouvelle avec current=true
    """
    try:
        # Terminer toute exécution encore "courante"
        await repo.update_job(
            item_id,
            {
                "$set": {
                    "metadata": {},
                    "executions.$[exec].current": False,
                    "executions.$[exec].finishedAt": datetime.utcnow()
                }
            },
            array_filters=[{"exec.current": True}]
        )

        # Ajouter une nouvelle exécution
        new_execution = {
            "startedAt": datetime.utcnow(),
            "finishedAt": None,
            "current": True,
            "errors": []
        }

        await repo.update_job(
            item_id,
            {"$push": {"executions": new_execution}}
        )

        print(f"🚀 Nouvelle exécution démarrée pour job {item_id}")

    except Exception as exc:
        print(f"❌ Impossible de démarrer une exécution pour {item_id} : {exc}")


async def finish_execution(item_id: str, status: str = "CLOSED"):
    """
    Termine l’exécution courante en ajoutant finishedAt
    et en mettant à jour le statut du job.
    """
    try:
        # ✅ Pause du job dans le scheduler
        scheduler = get_scheduler()
        scheduler.pause_job(job_id=item_id)
        print(f"⏸️ Job {item_id} mis en pause dans le scheduler.")
        result = await repo.update_job(
            item_id,
            {
                "$set": {
                    "executions.$[exec].current": False,
                    "executions.$[exec].finishedAt": datetime.utcnow(),
                    "status": status
                }
            },
            array_filters=[{"exec.current": True}]
        )

        if result.modified_count == 0:
            print(f"⚠️ Aucun job {item_id} trouvé avec une exécution courante.")
        else:
            print(f"✅ Exécution terminée pour job {item_id}, statut={status}")

    except Exception as exc:
        print(f"❌ Impossible de terminer l’exécution pour {item_id} : {exc}")


async def handle_error(item_id: str, exc: Exception, state: str):
    """
    Ajoute une erreur dans l’exécution courante.
    """
    error_entry = {
        "state": state,
        "message": str(exc),
        "timestamp": datetime.utcnow()
    }

    try:
        result = await repo.update_job(
            item_id,
            {
                "$push": {"executions.$[exec].errors": error_entry},
            },
            array_filters=[{"exec.current": True}]
        )

        if result.modified_count == 0:
            print(f"⚠️ Aucun job {item_id} trouvé avec une exécution courante.")
        else:
            print(f"⚠️ Erreur enregistrée pour job {item_id} : {error_entry}")
    except Exception as repo_exc:
        print(f"❌ Impossible de mettre à jour le job {item_id} : {repo_exc}")

async def update_execution(self, item_id: str, current_state: str = None, metadata: dict = None):
        update_query = {}
        if current_state:
            update_query["executions.$[exec].currentState"] = current_state

        if metadata:
            for key, value in metadata.items():
                update_query[f"executions.$[exec].metadata.{key}"] = value

        if not update_query:
            print(f"⚠️ Aucun champ à mettre à jour pour job {item_id}")
            return None

        try:
            result = await repo.update_job(
                item_id,
                {"$set": update_query},
                array_filters=[{"exec.current": True}]
            )
            if result.modified_count > 0:
                print(f"✅ Execution courante mise à jour pour {item_id} ({update_query})")
            else:
                print(f"⚠️ Aucun job {item_id} trouvé avec une exécution courante.")
            return result
        except Exception as exc:
            print(f"❌ Erreur update_execution sur {item_id} : {exc}")
            raise
