from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, confloat
from fastapi import APIRouter

router = APIRouter()


class FooBar(BaseModel):
    count: int
    size: float = None


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    not_given = "not_given"


class TemplateModuleRequest(BaseModel):
    """
    This is the description of the template module Request
    """

    foo_bar: FooBar = Field(...)
    gender: Gender = Field(None, alias="Gender")
    snap: int = Field(
        42,
        title="The Snap",
        description="this is the value of snap",
        ge=0,
        lt=100,
    )

    class Config:
        title = "Template Module Request"


class TemplateModuleResponse(BaseModel):
    """
    This is the description of the template module Response
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Template Module Response"


def build_response(
    request: TemplateModuleRequest,
) -> TemplateModuleResponse:
    """Build API response"""
    total_carbon = 0.5 * request.snap
    return TemplateModuleResponse(total_carbon_kg=total_carbon)


@router.post("/template", response_model=TemplateModuleResponse)
def template_module(request: TemplateModuleRequest) -> TemplateModuleResponse:
    """Calculate CO2 emissions for a template module"""
    response = build_response(request)
    return response


def interface() -> list[dict[str, Any]]:
    return [request(), response()]


def request() -> dict[str, Any]:
    return TemplateModuleRequest.schema()


def response() -> dict[str, Any]:
    return TemplateModuleResponse.schema()
