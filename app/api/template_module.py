from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
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

    class Config:
        title = "Template Module Response"


def interface() -> list[dict[str, Any]]:
    return [TemplateModuleRequest.schema(), TemplateModuleResponse.schema()]


def request() -> dict[str, Any]:
    return TemplateModuleRequest.schema()


def response() -> dict[str, Any]:
    return TemplateModuleResponse.schema()
