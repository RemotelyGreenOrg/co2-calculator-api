import statistics

from fastapi import APIRouter
from pydantic import BaseModel, conlist, confloat
from typing import Any

from app.api.modules import modules
from app.api import vc_calculator

# Todo: perform input sanity check and handle module errors per module


router = APIRouter()


class CostItem(BaseModel):
    module: str
    properties: Any


class CostPath(BaseModel):
    title: str
    cost_items: conlist(CostItem, min_items=1)


class CostAggregatorRequest(BaseModel):
    cost_paths: conlist(CostPath, min_items=1)


class CostItemResponse(BaseModel):
    cost_item: CostItem


class CostPathResponse(BaseModel):
    title: str
    total_carbon_kg: confloat(ge=0.0)
    cost_items: conlist(CostItemResponse)


class CostAggregatorResponse(BaseModel):
    cost_paths: conlist(CostPathResponse)


@router.post("/cost_aggregator")
async def cost_aggregator(request: CostAggregatorRequest) -> CostAggregatorResponse:
    cost_paths = []
    modules_by_name = modules.modules_by_name

    for cost_path in request.cost_paths:
        cost_items = []
        total_carbon_kg = 0.0

        for cost_item in cost_path.cost_items:
            if cost_item.module in modules_by_name:
                module = modules_by_name[cost_item.module]
                request = module.request_type(**cost_item.properties)
                response = module.entrypoint(request)

                if cost_item.module == vc_calculator.module.name:
                    emissions = response.total_emissions
                    total_carbon_kg += statistics.mean([emissions.low, emissions.high])
                else:
                    total_carbon_kg += response.total_carbon_kg

            cost_items.append(CostItemResponse(cost_item=cost_item))

        cost_paths.append(
            CostPathResponse(
                cost_items=cost_items,
                title=cost_path.title,
                total_carbon_kg=total_carbon_kg,
            )
        )

    return CostAggregatorResponse(cost_paths=cost_paths)
