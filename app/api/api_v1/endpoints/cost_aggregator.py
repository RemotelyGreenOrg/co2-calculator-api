from typing import Any, Generic

import pydantic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conlist, confloat
from pydantic.generics import GenericModel

from app.api.api_v1.calculator_interface import CalculatorInterface, RequestT, ResponseT
from app.api.api_v1.calculators import calculators

router = APIRouter()


class CostItem(BaseModel):
    calculator_name: str
    request: Any


class CostItemValidated(GenericModel, Generic[ResponseT, RequestT]):
    item: CostItem
    calculator: CalculatorInterface[ResponseT, RequestT]
    request: RequestT


class CostPath(BaseModel):
    title: str
    cost_items: conlist(CostItem, min_items=1)


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
    calculators_by_name = calculators.calculators_by_name
    cost_paths_validated = []
    errors = []

    for cost_path in cost_paths:
        title = cost_path.title
        cost_items_validated = []

        for cost_item in cost_path.cost_items:
            try:
                calculator = calculators_by_name[cost_item.calculator_name]
                request = calculator.request_model(**cost_item.request)
                validated_item = CostItemValidated(
                    item=cost_item, calculator=calculator, request=request
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
                        "error": f"Unknown calculator: ({error})",
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
            item, calculator = cost_item.item, cost_item.calculator
            response = await calculator.entrypoint(cost_item.request)
            total_carbon_kg += calculator.get_total_carbon_kg(response)
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
