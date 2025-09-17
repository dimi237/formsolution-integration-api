from datetime import datetime
from app.repositories.stats_repository import StatsRepository

class StatsService:
    def __init__(self):
        self.repo = StatsRepository()

    async def get_global_stats(self):
        stats =  await self.repo.get_global_stats()
        return stats
    async def get_activity_evolution(self, year: int = None):
        if not year:
            year = datetime.now().year

        # Définir plage de 10 ans (année courante -4 à +5)
        start_year = year - 9
        end_year = year 

        dossiers_by_month = await self.repo.count_dossiers_per_month(year)
        docs_by_month = await self.repo.count_docs_per_month(year)

        dossiers_by_year = await self.repo.count_dossiers_per_year(start_year, end_year)
        docs_by_year = await self.repo.count_docs_per_year(start_year, end_year)

        return {
            "year": year,
            "monthly": {
                "dossiers": {m: dossiers_by_month.get(m, 0) for m in range(1, 13)},
                "documents": {m: docs_by_month.get(m, 0) for m in range(1, 13)},
            },
            "yearly": {
                "dossiers": {y: dossiers_by_year.get(y, 0) for y in range(start_year, end_year + 1)},
                "documents": {y: docs_by_year.get(y, 0) for y in range(start_year, end_year + 1)},
            }
        }