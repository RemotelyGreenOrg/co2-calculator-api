from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


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


def interface():
    return [AnotherModuleRequest.schema(), AnotherModuleResponse.schema()]


def request():
    return AnotherModuleRequest.schema()


def response():
    return AnotherModuleResponse.schema()
