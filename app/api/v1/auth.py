from fastapi import APIRouter
from typing import List
from app.controllers.auth_controller import AuthController
from app.models.auth_model import TokenResponse
from app.models.dossier_model import DossierInDB

router = APIRouter()

controller = AuthController()

router.post("/login")(controller.login)
router.get("/refresh")(controller.refresh)
            