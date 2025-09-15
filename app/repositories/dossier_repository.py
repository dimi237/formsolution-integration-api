from datetime import datetime
from typing import Optional, List
from app.core.db import get_db
from app.models.dossier_model import DossierInDB, DossierStatus, FileMetadata

class DossierRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["dossiers"]

    async def create_dossier(self, dossier: DossierInDB):
        dossier.update({
            "status": DossierStatus.RUNNING,
            "files": [],
            "created_at": datetime.utcnow()
        })
        result = await self.collection.insert_one(dossier)
        return result

    async def get_by_uuid(self, uuid: str) -> Optional[DossierInDB]:
        data = await self.collection.find_one({"uuid": uuid})
        if data:
            return DossierInDB(**data)
        return None

    async def update_status(self, uuid: str, status: str):
        result = await self.collection.update_one(
            {"uuid": uuid},
            {"$set": {"status": status}}
        )
        return result.modified_count > 0

    async def add_file_metadata(self, uuid: str, file_metadata: dict):
        """Ajoute un fichier dans le tableau `files`."""
        result = await self.collection.update_one(
            {"uuid": uuid},
            {"$push": {"files": file_metadata}}
        )
        return result.modified_count > 0
    async def add_files(self, uuid: str, files: List[FileMetadata]):
        result = await self.collection.update_one(
            {"uuid": uuid},
            {"$set": {"files": files}}
        )
        return result.modified_count > 0

    async def update_file_upload(self, uuid: str, filename: str, drive_id: str):
        """Met à jour un fichier spécifique dans le tableau files."""
        result = await self.collection.update_one(
            {"uuid": uuid, "files.filename": filename},
            {
                "$set": {
                    "files.$.uploaded": True,
                    "files.$.uploadedAt": datetime.utcnow(),
                    "files.$.driveId": drive_id
                }
            }
        )
        return result.modified_count > 0
    async def update_file_download(self, uuid: str, filename: str):
        """Met à jour un fichier spécifique dans le tableau files."""
        result = await self.collection.update_one(
            {"uuid": uuid, "files.filename": filename},
            {
                "$set": {
                    "files.$.downloaded": True,
                    "files.$.downloadedAt": datetime.utcnow(),
                }
            }
        )
        return result.modified_count > 0

    async def list_dossiers(self, status: Optional[str] = None) -> List[DossierInDB]:
        query = {}
        if status:
            query["status"] = status
        cursor = self.collection.find(query)
        return [DossierInDB(**doc) async for doc in cursor]
        
    async def get_dossier_with_job(self, uuid: str):
        pipeline = [
            {"$match": {"uuid": uuid}},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "app_name",
                    "foreignField": "app_name",
                    "as": "job"
                }
            },
            {"$unwind": {"path": "$job", "preserveNullAndEmptyArrays": True}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0] if result else None
        
def get_repo():
    return DossierRepository()