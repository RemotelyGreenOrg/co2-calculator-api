from enum import Enum

from pydantic import BaseModel, Field, confloat

from app.api.api_v1.calculator_interface import CalculatorInterface


class FooBar(BaseModel):
    count: int
    size: float = None


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    not_given = "not_given"


class TemplateCalculatorRequest(BaseModel):
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
        title = "Template Calculator Request"


class TemplateCalculatorResponse(BaseModel):
    """
    This is the description of the template module Response
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Template Calculator Response"


async def entrypoint(request: TemplateCalculatorRequest) -> TemplateCalculatorResponse:
    return TemplateCalculatorResponse(total_carbon_kg=0.5 * request.snap)


module = CalculatorInterface(
    name="template_calculator",
    path="/template-calculator",
    entrypoint=entrypoint,
    request_model=TemplateCalculatorRequest,
    response_model=TemplateCalculatorResponse,
    get_total_carbon_kg=lambda request: request.total_carbon_kg,
)
