import asyncio
import httpx
from app.models.dossier_model import DossierStatus
from app.repositories.dossier_repository import DossierRepository, get_repo
from app.scripts.download_documents import process_item_cron
from app.settings import Settings
from app.utils.handle_execution import handle_error  # si tu veux tracer les erreurs côté jobs

settings = Settings()

async def fetch_files(item_id: str):
    print(f"🔄 Récupération des fichiers pour item_id={item_id}...")
    """Récupère la liste des fichiers depuis l'API externe."""
    url = f"{settings.BASE_URL}/file"
    params = {
        "application.name": item_id,
        "workflowStatus": "DONE"
    }
    try:
        async with httpx.AsyncClient(auth=(settings.API_USERNAME, settings.API_PASSWORD), timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            print(f"🔄 Réponse reçue du guichet")
            if not isinstance(data, list):
                raise ValueError(f"Réponse inattendue de l'API : {data}")
            return data
    except Exception as exc:
        print(f"❌ Erreur lors de la récupération des fichiers pour {item_id}: {exc}")
        raise
async def get_dossier(item_id: str, uuid: str, repo:DossierRepository) -> bool:
    found = await repo.get_by_uuid(uuid)
    if found is None:
            print(f"⬇️ Téléchargement de l'élément {uuid} (non trouvé en DB).")
            try:
                dossier = {
                    "uuid": uuid,
                    "app_name": item_id
                }
                found = await repo.create_dossier(dossier) 
                return True
            except Exception as err:
                print(f"❌ Erreur lors de la creation du dossier {uuid}: {err}")
                await handle_error(uuid, err, state=f"CREATE_FOLDER_FAILED_{uuid}")
    elif found.status != DossierStatus.DONE:
            print(f"✅ Élément {uuid} déjà présent en DB. Mais pas terminé (status={found.status}), on le reprocess.")
            await repo.update_status(uuid, DossierStatus.RUNNING) 
            return True
    print(f"✅ Élément {uuid} déjà présent en DB et terminé (status={found.status}), on skip.")
    return False
async def process_files(item_id: str):
    """Processus principal : boucle sur les fichiers, vérifie en base et télécharge si nécessaire."""
    print(f"🔄 debut du process pour item_id={item_id}...")
    
    try:
        files = await fetch_files(item_id)
        print(f"🔄 traitement des fichiers")
        
        if not files:
            print(f"ℹ️ Aucun fichier trouvé pour item_id={item_id}.")
            return

        repo = get_repo()
        for file in files:
            uuid = file.get("uuid")
            if not uuid:
                print("⚠️ Un élément du tableau n'a pas de champ 'uuid', ignoré.")
                continue
            if await get_dossier(item_id, uuid, repo):
                print(f"⬇️ Téléchargement des fichiers pour dossier {uuid}...")
                await process_item_cron(uuid)
                await repo.update_status(uuid, DossierStatus.DONE) 
                print(f"✅ Téléchargement terminé pour dossier {uuid}.")
                
    except Exception as exc:
        print(f"❌ Erreur critique dans process_files pour {item_id}: {exc}")
        await handle_error(item_id, exc, state=f"PROCESS_FILES_FAILED")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python process_files.py <item_id>")
    else:
        asyncio.run(process_files(sys.argv[1]))