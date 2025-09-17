from fastapi import Depends, HTTPException, Query
from app.services.stats_service import StatsService

class StatController:

    def get_service()-> StatsService:
       return StatsService()
    async def get_global_stats(self, service: StatsService = Depends(get_service)):
        try:
            return await service.get_global_stats()
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
    async def get_activity_evolution(self, year: int = Query(None, description="Année au format YYYY (par défaut: année courante)"), service: StatsService = Depends(get_service)):
        try:
            return await service.get_activity_evolution(year)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
