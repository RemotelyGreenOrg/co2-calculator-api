from typing import Optional

from pydantic import BaseModel


# Shared properties
class EventBase(BaseModel):
    name: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None


# Properties to receive on event creation
class EventCreate(EventBase):
    name: str
    lon: float
    lat: float


# Properties to receive on update
class EventUpdate(EventBase):
    pass


# Properties shared by models stored in DB
class EventInDBBase(EventBase):
    id: int
    name: str
    lon: float
    lat: float

    class Config:
        orm_mode = True


# Properties stored in DB
class EventInDB(EventInDBBase):
    pass


# Properties to return to client
class Event(EventInDBBase):
    pass
