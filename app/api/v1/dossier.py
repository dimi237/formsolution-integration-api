from fastapi import APIRouter
from typing import List
from app.controllers.dossier_controller import DossierController
from app.models.dossier_model import DossierInDB

router = APIRouter()

controller = DossierController()

router.get("/", response_model=List[DossierInDB])(controller.list_dossiers)
router.patch("/{uuid}/status")(controller.update_status)
router.get("/{uuid}")(controller.get_dossier)
            