from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter()

class another_moduleRequest(BaseModel):
    """
    This is the description of another module Request
    """
    monitors: int = Field(
        42,
        title='# Monitors',
        description='Number of monitors connected to PC',
        ge=1,
        lt=6,
    )

    class Config:
        title = 'Another Module Request'

class another_moduleResponse(BaseModel):
    """
    This is the description of another module Response
    """

    class Config:
        title = 'Another Module Response'

def interface():
    return [another_moduleRequest.schema(),another_moduleResponse.schema()]

def request():
    return another_moduleRequest.schema()

def response():
    return another_moduleResponse.schema()