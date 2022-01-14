from enum import Enum
from pydantic import BaseModel, Field

class another_module(BaseModel):
    """
    This is the description of another module
    """
    snap: int = Field(
        42,
        title='# Monitors',
        description='Number of monitors connected to screen',
        ge=1,
        lt=6,
    )

    class Config:
        title = 'Another Module'

def interface():
    return another_module.schema()
