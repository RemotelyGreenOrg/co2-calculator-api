from typing import Any, Generic

import pydantic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conlist, confloat
from pydantic.generics import GenericModel

from app.api.api_v1.module_interface import ModuleInterface, RequestT, ResponseT
from app.api.api_v1.modules import modules

router = APIRouter()


class CostItem(BaseModel):
    module: str
    properties: Any


class CostPath(BaseModel):
    title: str
    cost_items: conlist(CostItem, min_items=1)


class CostItemValidated(GenericModel, Generic[ResponseT, RequestT]):
    item: CostItem
    module: ModuleInterface[ResponseT, RequestT]
    request: RequestT


class CostPathValidated(CostPath):
    cost_items: conlist(CostItemValidated, min_items=1)


class CostAggregatorRequest(BaseModel):
    cost_paths: conlist(CostPath, min_items=1)


class CostItemResponse(BaseModel):
    cost_item: CostItem
    response: Any


class CostPathResponse(BaseModel):
    title: str
    total_carbon_kg: confloat(ge=0.0)
    cost_items: conlist(CostItemResponse)


class CostAggregatorResponse(BaseModel):
    cost_paths: conlist(CostPathResponse)


def validate_request_paths(cost_paths: list[CostPath]) -> list[CostPathValidated]:
    modules_by_name = modules.modules_by_name
    cost_paths_validated = []
    errors = []

    for cost_path in cost_paths:
        title = cost_path.title
        cost_items_validated = []

        for cost_item in cost_path.cost_items:
            try:
                module = modules_by_name[cost_item.module]
                request = module.request_model(**cost_item.properties)
                validated_item = CostItemValidated(
                    item=cost_item, module=module, request=request
                )
                cost_items_validated.append(validated_item)
            except pydantic.ValidationError as error:
                errors.append(
                    {
                        "title": title,
                        "cost_item": cost_item.dict(),
                        "error_type": "pydantic.ValidationError",
                        "error": error.errors(),
                    }
                )
            except KeyError as error:
                errors.append(
                    {
                        "title": title,
                        "cost_item": cost_item.dict(),
                        "error_type": "KeyError",
                        "error": f"Unknown module: ({error})",
                    }
                )

        if len(cost_items_validated) != 0:
            cost_paths_validated.append(
                CostPathValidated(title=title, cost_items=cost_items_validated)
            )

    if len(errors) != 0:
        raise HTTPException(status_code=422, detail=errors)

    return cost_paths_validated


@router.post("/cost-aggregator")
async def cost_aggregator(request: CostAggregatorRequest) -> CostAggregatorResponse:
    cost_paths = validate_request_paths(request.cost_paths)
    cost_path_responses = []

    for cost_path in cost_paths:
        cost_item_responses = []
        total_carbon_kg = 0.0

        for cost_item in cost_path.cost_items:
            item, module = cost_item.item, cost_item.module
            response = await module.entrypoint(cost_item.request)
            total_carbon_kg += module.get_total_carbon_kg(response)
            item_response = CostItemResponse(cost_item=item, response=response)
            cost_item_responses.append(item_response)

        cost_path_responses.append(
            CostPathResponse(
                cost_items=cost_item_responses,
                title=cost_path.title,
                total_carbon_kg=total_carbon_kg,
            )
        )

    return CostAggregatorResponse(cost_paths=cost_path_responses)
