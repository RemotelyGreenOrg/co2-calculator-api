from enum import Enum
from pydantic import BaseModel, Field

class FooBar(BaseModel):
    count: int
    size: float = None


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'

class template_module(BaseModel):
    """
    This is the description of the template module
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
        title = 'Template Module'

def interface():
    return template_module.schema()
