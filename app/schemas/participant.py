from typing import Optional

from pydantic import BaseModel

from app.schemas.common import JoinMode


# Shared properties
class ParticipantBase(BaseModel):
    join_mode: Optional[JoinMode] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    active: Optional[bool] = None
    event_id: Optional[int] = None


# Properties to receive on country creation
class ParticipantCreate(ParticipantBase):
    join_mode: JoinMode
    lon: float
    lat: float
    active: bool = True
    event_id: int


# Properties to receive on update
class ParticipantUpdate(ParticipantBase):
    pass


# Properties shared by models stored in DB
class ParticipantInDBBase(ParticipantBase):
    id: int
    join_mode: JoinMode
    lon: float
    lat: float
    active: bool
    event_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Participant(ParticipantInDBBase):
    pass


# Properties properties stored in DB
class ParticipantInDB(ParticipantInDBBase):
    pass
