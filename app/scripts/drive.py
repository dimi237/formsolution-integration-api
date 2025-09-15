import os
import shutil
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.settings import Settings
from app.repositories.job_repository import get_repo as get_job_repo
from app.repositories.dossier_repository import get_repo
from app.models.job_model import JobInDB
from app.utils.datetime import now_timestamp
from app.utils.handle_execution import finish_execution, handle_error, update_execution

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']

settings = Settings()


async def upload_folder_and_files_to_drive(uuid: str, folder_name:str):
    """
    Récupère le job en DB avec uuid,
    upload le dossier sur Google Drive,
    puis supprime le dossier local et met à jour le statut du job.
    """
    repo = get_repo()
    job_repo = get_job_repo()
    dossier = await repo.get_by_uuid(uuid)
    job = await job_repo.get_by_item_id(dossier.app_name) if dossier else None
    print(f"🔄 Début upload_folder_and_files_to_drive pour {dossier}...")

    if not dossier:
        print(f"❌ Job de  {uuid} introuvable.")
        return

    folder_id = job.folder_id
    folder_path = os.path.join(settings.DOWNLOAD_DIR, folder_name)

    try:
        # Authentification Google
        creds = service_account.Credentials.from_service_account_file(
            settings.CREDENTIAL_PATH, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=creds)
        print("✅ Authentification réussie.")

        if not os.path.exists(folder_path):
            print(f"❌ Dossier local '{folder_path}' introuvable.")
            return

        # Création du dossier sur Google Drive
        print(f"📂 Création du dossier '{folder_name}' sur Google Drive...")
        file_metadata = {
            'name': f'{folder_name}_{now_timestamp()}',
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(
            body=file_metadata,
            fields='id',  
            supportsAllDrives=True
        ).execute()

        new_drive_folder_id = folder.get('id')
        print(f"✅ Dossier créé : {new_drive_folder_id}")
        filesUploaded = []

        # Upload des fichiers
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                try:
                    print(f"⬆️ Upload de {filename}...")
                    file_metadata = {
                        'name': filename,
                        'parents': [new_drive_folder_id]
                    }
                    media = MediaFileUpload(file_path, resumable=True)
                    file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id',
                        supportsAllDrives=True
                    ).execute()
                    filesUploaded.append({
                        'filename':filename,
                        'drive_id': file.get('id'),
                        'folder_path':folder_path,
                        'folder_id':new_drive_folder_id
                        
                    })
                    await repo.update_file_upload(uuid, filename, file.get('id'))
                    print(f"✅ {filename} uploadé, ID : {file.get('id')}")
                except Exception as e:
                    print(f"❌ Erreur upload {filename} : {e}")
                    await handle_error(uuid, e, f"UPLOAD:{filename}")
                    
        # await update_execution(uuid, "UPLOAD_DOCUMENTS", filesUploaded)
        # ✅ Suppression du dossier local
        shutil.rmtree(folder_path)
        print(f"🗑️ Dossier {folder_path} supprimé.")        
        await finish_execution(job.item_id)
        print(f"✅ Déùarche {uuid} passé en statut CLOSED.")

    except Exception as e:
        print(f"❌ Erreur dans upload_folder_and_files_to_drive : {e}")
        await handle_error(uuid, e, 'UPLOAD_TO_DRIVE')
