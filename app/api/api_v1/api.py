"""Register API routers and modules"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import countries, cost_aggregator, health_check, websocket
from app.api.api_v1.modules import modules

api_router = APIRouter()

api_router.include_router(health_check.router, tags=["health_check"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(cost_aggregator.router, tags=["cost-aggregator"])
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])

modules.register(api_router)
