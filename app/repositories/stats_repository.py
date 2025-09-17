from datetime import datetime
from app.core.db import get_db

class StatsRepository:
    def __init__(self):
        self.db = get_db()
        self.jobs = self.db.jobs
        self.dossiers = self.db.dossiers

    async def get_global_stats(self):
        # Nombre total de jobs
        total_jobs = await self.jobs.count_documents({})

        # Nombre total de dossiers
        total_dossiers = await self.dossiers.count_documents({})

        # Nombre total de fichiers transférés (files.uploaded = true)
        pipeline = [
            {"$unwind": "$files"},
            {"$match": {"files.uploaded": True}},
            {"$count": "total_uploaded_files"}
        ]
        result = await self.dossiers.aggregate(pipeline).to_list(length=1)
        total_uploaded_files = result[0]["total_uploaded_files"] if result else 0

        return {
            "total_jobs": total_jobs,
            "total_dossiers": total_dossiers,
            "total_uploaded_files": total_uploaded_files
        }
    async def count_dossiers_per_month(self, year: int):
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lte": datetime(year, 12, 31, 23, 59, 59)
                    }
                }
            },
            {
                "$group": {
                    "_id": {"month": {"$month": "$created_at"}},
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await self.db.dossiers.aggregate(pipeline).to_list(None)
        return {r["_id"]["month"]: r["count"] for r in results}

    async def count_docs_per_month(self, year: int):
        pipeline = [
            {"$unwind": "$files"},
            {"$match": {
                "files.uploaded": True,
                "files.uploadedAt": {
                    "$gte": datetime(year, 1, 1),
                    "$lte": datetime(year, 12, 31, 23, 59, 59)
                }
            }},
            {
                "$group": {
                    "_id": {"month": {"$month": "$files.uploadedAt"}},
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await self.db.dossiers.aggregate(pipeline).to_list(None)
        return {r["_id"]["month"]: r["count"] for r in results}

    async def count_dossiers_per_year(self, start_year: int, end_year: int):
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": datetime(start_year, 1, 1),
                        "$lte": datetime(end_year, 12, 31, 23, 59, 59)
                    }
                }
            },
            {
                "$group": {
                    "_id": {"year": {"$year": "$created_at"}},
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await self.db.dossiers.aggregate(pipeline).to_list(None)
        return {r["_id"]["year"]: r["count"] for r in results}

    async def count_docs_per_year(self, start_year: int, end_year: int):
        pipeline = [
            {"$unwind": "$files"},
            {"$match": {
                "files.uploaded": True,
                "files.uploadedAt": {
                    "$gte": datetime(start_year, 1, 1),
                    "$lte": datetime(end_year, 12, 31, 23, 59, 59)
                }
            }},
            {
                "$group": {
                    "_id": {"year": {"$year": "$files.uploadedAt"}},
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await self.db.dossiers.aggregate(pipeline).to_list(None)
        return {r["_id"]["year"]: r["count"] for r in results}
