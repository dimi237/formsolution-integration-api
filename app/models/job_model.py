from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobBase(BaseModel):
    item_id: str = Field(..., description="Identifiant unique de l’item")
    name: str = Field(..., description="Nom du job")
    folder_id: str = Field(..., description="Id du dossier associé dans drive")


class JobCreate(JobBase):
    frequency: int = Field(..., description="Fréquence d’exécution en secondes")


class JobInDB(JobBase):
    id: str = Field(..., alias="_id")
    status: str = Field(default="running", description="Statut du job")
    frequency: int
    created_at: str = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "item_id": "12345",
                "name": "Téléchargement docs",
                "folder_id": "compte_demo",
                "frequency": 60,
                "status": "running",
                "created_at": "2025-09-06T10:00:00"
            }
        }
