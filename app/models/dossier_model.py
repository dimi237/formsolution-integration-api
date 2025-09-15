from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FileMetadata(BaseModel):
    filename: str
    downloaded: bool = False
    uploaded: bool = False
    uploadedAt: Optional[datetime] = None
    downloadedAt: Optional[datetime] = None
    driveId: Optional[str] = None

class DossierInDB(BaseModel):
    uuid: str
    app_name: str = Field(..., alias="appName")
    status: str
    files: List[FileMetadata] = []
    date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class DossierStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CLOSED = "CLOSED"