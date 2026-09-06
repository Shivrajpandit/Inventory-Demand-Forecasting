"""
Master API Router
=================
"""

from fastapi import APIRouter

from backend.app.api.auth_routes import router as auth_router
from backend.app.api.product_routes import router as product_router
from backend.app.api.dashboard_routes import router as dashboard_router
from backend.app.api.forecast_routes import router as forecast_router
from backend.app.api.inventory_routes import router as inventory_router
from backend.app.api.scenario_routes import router as scenario_router
from backend.app.api.model_routes import router as model_router
from backend.app.api.upload_routes import router as upload_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(product_router)
api_router.include_router(dashboard_router)
api_router.include_router(forecast_router)
api_router.include_router(inventory_router)
api_router.include_router(scenario_router)
api_router.include_router(model_router)
api_router.include_router(upload_router)
