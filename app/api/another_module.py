from pydantic import BaseModel, Field

from app.api.module_interface import ModuleInterface


class AnotherModuleRequest(BaseModel):
    """
    This is the description of another module Request
    """

    monitors: int = Field(
        42,
        title="# Monitors",
        description="Number of monitors connected to PC",
        ge=1,
        lt=6,
    )

    class Config:
        title = "Another Module Request"


class AnotherModuleResponse(BaseModel):
    """
    This is the description of another module Response
    """

    class Config:
        title = "Another Module Response"


async def entrypoint(request: AnotherModuleRequest) -> AnotherModuleResponse:
    return AnotherModuleResponse()


module = ModuleInterface(
    name="another_module",
    path="/another-module",
    entrypoint=entrypoint,
    request_model=AnotherModuleRequest,
    response_model=AnotherModuleResponse,
    get_total_carbon_kg=lambda: 0,
)
