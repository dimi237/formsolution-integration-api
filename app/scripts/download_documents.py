import sys
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from app.scripts.upload import upload_folder_and_files_to_drive
from app.settings import Settings 

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

async def fetch_item(client: httpx.AsyncClient, item_id: str):
    url = f"{settings.BASE_URL}/file/{item_id}"
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        print(f"✅ Récupération réussie pour l'item {item_id}")
        return resp.json()
    except httpx.ConnectTimeout:
        print(f"⏱ Erreur : délai de connexion dépassé pour {url}")
    except httpx.ConnectError:
        print(f"❌ Erreur : impossible de se connecter à {url}")
    except httpx.HTTPStatusError as exc:
        print(f"⚠️ Erreur HTTP {exc.response.status_code} pour {url} : {exc.response.text[:200]}")
    except Exception as exc:
        print(f"❗ Erreur inattendue pour {url} : {exc}")
        
async def download_file(client: httpx.AsyncClient, url: str, dest_path: Path):
    resp = await client.get(url)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    print(f"✅ Fichier téléchargé : {dest_path}")

async def main(item_id: str, folder_id:str):
    async with httpx.AsyncClient(timeout=10.0,auth=(settings.API_USERNAME, settings.API_PASSWORD)) as client:
        data = await fetch_item(client, item_id)
        # print(data)
        if data:
            try:
                if data.get("workflowStatus") != "VALIDATION":
                    print(f"❌ Item {item_id} ignoré (workflowStatus != VALIDATION)")
                    return

                item_name = data.get("application").get("name", f"item_{item_id}")
                base_dir = Path(settings.DOWNLOAD_DIR) / item_name
                base_dir.mkdir(parents=True, exist_ok=True)

                tasks = []
                for doc in data.get("documents", []):
                    doc_uuid = doc["uuid"]
                    for idx, file in enumerate(doc.get("files", [])):
                        filename = file.get("fileName", f"{doc_uuid}_{idx}")
                        dest_path = base_dir / filename
                        file_url = f"{settings.BASE_URL}/document/ds/{item_id}/attachment/{doc_uuid}/file/{idx + 1}"
                        tasks.append(download_file(client, file_url, dest_path))

                await asyncio.gather(*tasks)
                upload_folder_and_files_to_drive(folder_id, item_name)
            except Exception as exc:
                print(f"❌ Impossible de sauvegarder le fichier  : {exc}")

def process_item():
    try:
        item_id = sys.argv[1]
        asyncio.run(main(item_id))
    except Exception as exc:
        print("❌ Erreur critique lors du téléchargement :", exc)
def process_item_cron(item_id, folder_id):
    try:
        asyncio.run(main(item_id, folder_id))
    except Exception as exc:
        print("❌ Erreur critique lors du téléchargement :", exc)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_documents.py <item_id>")
    else:
        process_item()
