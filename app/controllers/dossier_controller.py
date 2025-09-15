from fastapi import HTTPException, Depends
from app.models.dossier_model import DossierInDB
from app.services.dossier_service import DossierService

class DossierController:

    def get_service():
       return DossierService()

    async def get_dossier(uuid: str, service: DossierService = Depends(get_service)):
        dossier = await service.get_dossier(uuid)
        if not dossier:
            raise HTTPException(status_code=404, detail="Dossier not found")
        return dossier

    async def update_status(uuid: str, status: str, service: DossierService = Depends(get_service)):
        return await service.update_status(uuid, status)

    async def list_dossiers(status: str = None, service: DossierService = Depends(get_service)):
        return await service.list_dossiers(status)
