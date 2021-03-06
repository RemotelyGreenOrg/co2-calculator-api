"""Register API routers and modules"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    cost_aggregator,
    countries,
    event_cost_aggregator,
    events,
    health_check,
    participants,
    websocket,
)
from app.api.api_v1.calculators import calculators

api_router = APIRouter()

api_router.include_router(
    health_check.router,
    tags=["health_check"],
)
api_router.include_router(
    websocket.router,
    tags=["websocket"],
)
api_router.include_router(
    cost_aggregator.router,
    tags=["cost-aggregator"],
)
api_router.include_router(
    countries.router,
    prefix="/countries",
    tags=["countries"],
)
api_router.include_router(
    events.router,
    prefix="/events",
    tags=["events"],
)
api_router.include_router(
    event_cost_aggregator.router,
    prefix="/event-cost-aggregator",
    tags=["events", "cost-aggregator"],
)
api_router.include_router(
    participants.router,
    prefix="/participants",
    tags=["participants"],
)

calculators.register(api_router)
