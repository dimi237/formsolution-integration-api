import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.settings import Settings 

load_dotenv() 

required_settings = ["CREDENTIAL_PATH", "DOWNLOAD_DIR"]

try:
    settings = Settings()
except Exception as exc:
    print("❌ Impossible de charger les settings :", exc)
    raise SystemExit(1)

# L'ID du dossier Google Drive partagé de destination
# Vous pouvez trouver l'ID dans l'URL du dossier Drive : drive.google.com/drive/folders/ID_DU_DOSSIER
DRIVE_FOLDER_ID = '0AONNFIsEr8MtUk9PVA'

# Les Scopes nécessaires pour l'API Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_folder_and_files_to_drive(folder_id, name):
    """
    Crée un dossier sur Google Drive avec le même nom que le dossier local,
    puis télécharge tous les fichiers de ce dossier local vers le nouveau dossier Drive.
    """
    folder_path = os.path.join(settings.DOWNLOAD_DIR,name)
    try:
        # Authentification avec le compte de service
        creds = service_account.Credentials.from_service_account_file(
            settings.CREDENTIAL_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        print("Authentification réussie.")

        if not os.path.exists(folder_path):
            print(f"Erreur : Le dossier local '{folder_path}' n'existe pas.")
            return

        # Obtenir le nom du dossier local
        folder_name = os.path.basename(folder_path)

        # Créer le nouveau dossier sur Google Drive
        print(f"Création du dossier '{folder_name}' sur Google Drive...")
        file_metadata = {
            'name': folder_name,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=file_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()

        new_drive_folder_id = folder.get('id')
        print(f"Dossier '{folder_name}' créé avec succès. ID : {new_drive_folder_id}")
        
        # Parcourir les fichiers dans le dossier local et les uploader
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                print(f"Téléchargement de {filename}...")
                
                try:
                    file_metadata = {
                        'name': filename,
                        'parents': [new_drive_folder_id] # Upload vers le nouveau dossier
                    }
                    media = MediaFileUpload(file_path, resumable=True)
                    
                    file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id',
                        supportsAllDrives=True
                    ).execute()
                    
                    print(f"Fichier '{filename}' téléchargé avec succès. ID : {file.get('id')}")
                
                except Exception as e:
                    print(f"Erreur lors de l'upload de {filename} : {e}")
                    
    except Exception as auth_error:
        print(f"Erreur d'authentification ou de connexion à l'API : {auth_error}")

if __name__ == '__main__':
    upload_folder_and_files_to_drive(DRIVE_FOLDER_ID, '')