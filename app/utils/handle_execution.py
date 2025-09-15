# app/utils/execution_handler.py
from datetime import datetime
from typing import List
from app.core.scheduler import get_scheduler
from app.models.dossier_model import FileMetadata
from app.repositories.job_repository import get_repo
from app.repositories.dossier_repository import get_repo as get_dossier_repo



async def start_execution(uuid: str):
    repo = get_repo()
    dossier_repo = get_dossier_repo()
    """
    Démarre une nouvelle exécution : 
    - termine celle en cours (current=false, finishedAt=now)
    - ajoute une nouvelle avec current=true
    """
    try:
        # Terminer toute exécution encore "courante"
        dossier = await dossier_repo.get_by_uuid(uuid)
        if not dossier:
            print(f"❌ Aucun dossier trouvé avec le uuid {uuid}.")
            return
        item_id = dossier.app_name
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
            uuid,
            {"$push": {"executions": new_execution}}
        )

        print(f"🚀 Nouvelle exécution démarrée pour job {uuid}")

    except Exception as exc:
        print(f"❌ Impossible de démarrer une exécution pour {uuid} : {exc}")


async def finish_execution(item_id: str):
    """
    Termine l’exécution courante en ajoutant finishedAt
    et en mettant à jour le statut du job.
    """
    repo = get_repo()
    
    try:

        print(f"⏸️ Job {item_id} mis en pause dans le scheduler.")
        result = await repo.update_job(
            item_id,
            {
                "$set": {
                    "executions.$[exec].current": False,
                    "executions.$[exec].finishedAt": datetime.utcnow(),
                }
            },
            array_filters=[{"exec.current": True}]
        )

        if result.modified_count == 0:
            print(f"⚠️ Aucun job {item_id} trouvé avec une exécution courante.")
        else:
            print(f"✅ Exécution terminée pour job {item_id}")

    except Exception as exc:
        print(f"❌ Impossible de terminer l’exécution pour {item_id} : {exc}")


async def handle_error(uuid: str, exc: Exception, state: str):
    """
    Ajoute une erreur dans l’exécution courante.
    """
    error_entry = {
        "state": state,
        "message": str(exc),
        "timestamp": datetime.utcnow()
    }
    item_id = ''
    repo = get_repo()
    dossier_repo = get_dossier_repo()
    dossier = await dossier_repo.get_by_uuid(uuid)
    if dossier:
        item_id = dossier.app_name
    else:
        item_id = uuid  # Fallback si le dossier n'est pas trouvé
    if not item_id:
        return
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

async def update_execution(self, uuid: str, current_state: str = None, files: dict = None):
    """
    Met à jour l'exécution courante d'un job.
    - current_state : nouveau state
    - metadata : dictionnaire flexible pour ajouter des infos (liste, dict, str, etc.)
    """
    update_query = {}
    repo = get_repo()

    # Mise à jour du state si fourni
    if current_state:
        update_query["executions.$[exec].currentState"] = current_state

    try:
        result = await repo.update_job(
            uuid,
            {"$set": update_query},
            array_filters=[{"executions.$[exec].current": True}]
        )
        if result.modified_count > 0:
            print(f"✅ Execution courante mise à jour pour {uuid} ({update_query})")
        else:
            print(f"⚠️ Aucun job {uuid} trouvé avec une exécution courante.")
        return result
    except Exception as exc:
        print(f"❌ Erreur update_execution sur {uuid} : {exc}")
        raise
async def add_files_on_dossier(uuid: str, files: List[FileMetadata] ):
    """
    Ajoute un fichier téléchargé dans le dossier.
    """
    if files is None:
        return
    repo = get_dossier_repo()
    try:
        result = await repo.add_files(uuid, files)
        if result:
            print(f"✅ Fichiers ajouté au dossier {uuid}.")
        else:
            print(f"⚠️ Aucun dossier trouvé avec le uuid {uuid}.")
        return result
    except Exception as exc:
        print(f"❌ Impossible d'ajouter des fichers au dossier {uuid} : {exc}")
        raise
async def update_downloaded_file(uuid: str, filename: str):
    repo = get_dossier_repo()
    try:
        result = await repo.update_file_download(uuid, filename)
        if result:
            print(f"✅ Fichier {filename} mis 0 jour dans le dossier {uuid}.")
        else:
            print(f"⚠️ Aucun fichier {filename} trouvé  dans le dossier {uuid}.")
        return result
    except Exception as exc:
        print(f"❌ Impossible de mettre à jour le fichier {filename} dans le dossier dossier {uuid} : {exc}")
        raise