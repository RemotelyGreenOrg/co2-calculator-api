from enum import Enum

from pydantic import BaseModel, Field

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

    class Config:
        title = "Template Module Response"


async def entrypoint(request: TemplateModuleRequest) -> TemplateModuleResponse:
    return TemplateModuleResponse()


module = ModuleInterface(
    name="template_module",
    path="/template-module",
    entrypoint=entrypoint,
    request_model=TemplateModuleRequest,
    response_model=TemplateModuleResponse,
    get_total_carbon_kg=lambda: 0,
)
