from fastapi import APIRouter

from app.controllers.stats_controller import StatController

router = APIRouter()
controller = StatController()


router.get("/global")(controller.get_global_stats)
router.get("/charts")(controller.get_activity_evolution)
