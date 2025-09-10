import asyncio
from app.core.db import connect_to_mongo, close_mongo_connection
from app.repositories.job_repository import JobRepository
from app.models.job_model import JobCreate

import tracemalloc
tracemalloc.start()

async def test():
    await connect_to_mongo()

    repo = JobRepository()

    job = JobCreate(item_id="123", name="Test Job", account="demo", frequency=30)
    saved = await repo.create(job)
    print("✅ Saved:", saved)

    fetched = await repo.get_by_item_id("123")
    print("📌 Fetched:", fetched)

    updated = await repo.update_status("123", "paused")
    print("✏️ Updated:", updated)

    deleted = await repo.delete("123")
    print("🗑 Deleted:", deleted)

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(test())   # ✅ ici on exécute proprement l'async