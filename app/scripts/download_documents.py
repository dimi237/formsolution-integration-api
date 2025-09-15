import sys
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from app.scripts.drive import upload_folder_and_files_to_drive
from app.settings import Settings
from app.utils.handle_execution import add_files_on_dossier, handle_error, start_execution, update_downloaded_file, update_execution 

load_dotenv() 

required_settings = ["BASE_URL", "API_USERNAME", "API_PASSWORD", "DOWNLOAD_DIR"]

try:
    settings = Settings()
except Exception as exc:
    print("❌ Impossible de charger les settings :", exc)
    raise SystemExit(1)

missing = [s for s in required_settings if getattr(settings, s, None) in (None, "")]
if missing:
    print(f"⚠️ Les settings suivants sont manquants ou vides : {missing}")
    raise SystemExit(1)

download_path = Path(settings.DOWNLOAD_DIR)
if not download_path.exists():
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Dossier créé : {download_path}")
    except Exception as exc:
        print(f"❌ Impossible de créer le dossier {download_path} : {exc}")
        raise SystemExit(1)

async def fetch_item(client: httpx.AsyncClient, uuid: str):
    url = f"{settings.BASE_URL}/file/{uuid}"
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        print(f"✅ Récupération réussie pour l'item {uuid}")
        return resp.json()
    except httpx.ConnectTimeout:
        print(f"⏱ Erreur : délai de connexion dépassé pour {url}")
        await handle_error(uuid, httpx.ConnectTimeout, 'FETCH_ITEM')
    except httpx.ConnectError:
        print(f"❌ Erreur : impossible de se connecter à {url}")
        await handle_error(uuid, httpx.ConnectError, 'FETCH_ITEM')
    except httpx.HTTPStatusError as exc:
        print(f"⚠️ Erreur HTTP {exc.response.status_code} pour {url} : {exc.response.text[:200]}")
        await handle_error(uuid, exc, 'FETCH_ITEM')
    except Exception as exc:
        print(f"❗ Erreur inattendue pour {url} : {exc}")
        await handle_error(uuid, exc, 'FETCH_ITEM')
        
async def download_file(client: httpx.AsyncClient, url: str, dest_path: Path,uuid:str, filename:str):
    resp = await client.get(url)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    await update_downloaded_file(uuid, filename)
    print(f"✅ Fichier téléchargé : {dest_path}")

async def main(uuid: str):
    async with httpx.AsyncClient(timeout=10.0,auth=(settings.API_USERNAME, settings.API_PASSWORD)) as client:
        await start_execution(uuid)
        data = await fetch_item(client, uuid)
        if data:
            try:
                if data.get("workflowStatus") != "DONE":
                    print(f"❌ Item {uuid} ignoré (workflowStatus != DONE)")
                    return
                item_name = data.get("application").get("name", f"item_{uuid}")
                base_dir = Path(settings.DOWNLOAD_DIR) / item_name
                base_dir.mkdir(parents=True, exist_ok=True)
                tasks = []
                files = []
                for doc in data.get("documents", []):
                    doc_uuid = doc["uuid"]
                    for idx, file in enumerate(doc.get("files", [])):
                        filename = file.get("fileName", f"{doc_uuid}_{idx}")
                        dest_path = base_dir / filename
                        file_url = f"{settings.BASE_URL}/document/ds/{uuid}/attachment/{doc_uuid}/file/{idx + 1}"
                        tasks.append(download_file(client, file_url, dest_path, uuid, filename))
                        files.append({
                            "driveId": None,
                            "filename": filename,
                            "downloaded": False,
                            "downloadedAt": None,
                            "uploaded": False,
                            "uploadedAt": None
                        })

                await add_files_on_dossier(uuid, files)
                await asyncio.gather(*tasks)
                await upload_folder_and_files_to_drive(uuid, item_name)
            except Exception as exc:
                print(f"❌ Impossible de sauvegarder le fichier  : {exc}")
                await handle_error(uuid, exc, 'SAVE_FILE')

def process_item():
    try:
        uuid = sys.argv[1]
        asyncio.run(main(uuid))
    except Exception as exc:
        print("❌ Erreur critique lors du téléchargement :", exc)
async def process_item_cron(uuid):
    try:
        await main(uuid)
    except Exception as exc:
        print("❌ Erreur critique lors du téléchargement :", exc)
        await handle_error(uuid, exc, 'PROCESS_ITEM')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_documents.py <uuid>")
    else:
        process_item()
