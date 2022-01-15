from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter()

class FooBar(BaseModel):
    count: int
    size: float = None


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'

class template_moduleRequest(BaseModel):
    """
    This is the description of the template module Request
    """

    foo_bar: FooBar = Field(...)
    gender: Gender = Field(None, alias='Gender')
    snap: int = Field(
        42,
        title='The Snap',
        description='this is the value of snap',
        ge=0,
        lt=100,
    )

    class Config:
        title = 'Template Module Request'

class template_moduleResponse(BaseModel):
    """
    This is the description of the template module Response
    """

    class Config:
        title = 'Template Module Response'

def interface():
    return [template_moduleRequest.schema(),template_moduleResponse.schema()]

def request():
    return template_moduleRequest.schema()

def response():
    return template_moduleResponse.schema()