from enum import Enum

from pydantic import BaseModel, Field, confloat

from app.module_interface import ModuleInterface


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


async def entrypoint(request: TemplateModuleRequest) -> TemplateModuleResponse:
    return TemplateModuleResponse(total_carbon_kg=0.5 * request.snap)


module = ModuleInterface(
    name="template_module",
    path="/template-module",
    entrypoint=entrypoint,
    request_model=TemplateModuleRequest,
    response_model=TemplateModuleResponse,
    get_total_carbon_kg=lambda request: request.total_carbon_kg,
)
