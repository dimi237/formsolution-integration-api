# app/core/db.py
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from app.core.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo():
    """Initialise la connexion Mongo."""
    global client, db
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db_name]
    print("✅ MongoDB connecté")


async def close_mongo_connection():
    """Ferme la connexion Mongo."""
    global client
    if client:
        client.close()
        print("🛑 MongoDB déconnecté")
        
def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        raise RuntimeError("❌ MongoDB is not connected. Did you call connect_to_mongo() ?")
    return db