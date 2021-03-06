from typing import Optional, Union, Any, List

from pydantic import BaseModel
from pydantic.utils import GetterDict


# Shared properties
from starlette.websockets import WebSocket

from app.schemas.common import GeoCoordinates, JoinMode
from app.schemas.participant import Participant, ParticipantInDB


UID = str


class EventBase(BaseModel):
    name: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    participants: List[Participant] = []


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
    participants: List[ParticipantInDB] = []

    class Config:
        orm_mode = True


# Properties stored in DB
class EventInDB(EventInDBBase):
    pass


# Properties to return to client
class Event(EventInDBBase):
    pass
