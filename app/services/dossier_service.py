from typing import List, Optional
from app.models.dossier_model import DossierInDB, FileMetadata
from app.repositories.dossier_repository import DossierRepository

class DossierService:
    def __init__(self, repo: Optional[DossierRepository] = None):
        self.repo = repo or DossierRepository()

    async def create_dossier(self, dossier: DossierInDB) -> str:
        return await self.repo.create_dossier(dossier)

    async def get_dossier(self, uuid: str) -> Optional[DossierInDB]:
        return await self.repo.get_by_uuid(uuid)

    async def update_status(self, uuid: str, status: str) -> bool:
        return await self.repo.update_status(uuid, status)

    async def add_file(self, uuid: str, filename: str) -> bool:
        file_metadata = FileMetadata(filename=filename).model_dump()
        return await self.repo.add_file_metadata(uuid, file_metadata)

    async def mark_file_uploaded(self, uuid: str, filename: str, drive_id: str) -> bool:
        return await self.repo.update_file_upload(uuid, filename, drive_id)

    async def list_dossiers(self, status: Optional[str] = None) -> List[DossierInDB]:
        return await self.repo.list_dossiers(status)
