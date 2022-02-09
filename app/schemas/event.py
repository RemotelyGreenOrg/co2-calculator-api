from typing import Optional, Union, Any

from pydantic import BaseModel
from starlette.websockets import WebSocket

from app.schemas.common import GeoCoordinates, JoinMode


# Shared properties
class EventBase(BaseModel):
    name: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None


# Properties to receive on country creation
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


UID = str


class ParticipantModel(BaseModel):
    location: Union[GeoCoordinates, dict[str, str]]
    join_mode: JoinMode
    websocket: Any
    active: bool = True
    uid: Optional[UID] = None


class EventModelWebsocket:
    def __init__(self, name: str, location: Union[GeoCoordinates, str], calculator):
        self.name = name
        self.location = location
        self._participants = {}
        self.calculator = calculator

    @property
    def num_participants(self):
        return len(self._participants)

    @property
    def participants(self):
        return self._participants.values()

    @property
    def participant_locations(self):
        return [p.location for p in self._participants.values()]

    @property
    def all_uids(self):
        return [p.uid for p in self._participants.values()]

    async def add_participant(
        self,
        location: GeoCoordinates,
        join_mode: JoinMode,
        websocket: WebSocket,
        # TODO: uid: str = None
    ):
        # TODO: needs to be provided externally to have any meaning
        uid = str(self.num_participants)

        parti = self._participants.get(uid, None)
        if parti:
            parti.active = True
            parti.websocket = websocket
        else:
            parti = ParticipantModel(
                location=location,
                join_mode=JoinMode[join_mode],
                websocket=websocket,
                active=True,
                uid=uid,
            )
            self._participants[uid] = parti

        await self.update_sockets()

    async def remove_participant(self, websocket: WebSocket):
        # TODO: This should work of UID not websockets...
        for participant in self._participants.values():
            if participant.websocket == websocket:
                participant.active = False
                participant.websocket = None

        await self.update_sockets()

    async def update_sockets(self):
        results = await self.calculator(self)

        for participant in self._participants.values():
            if not participant.active:
                continue
            await participant.websocket.send_json(
                {
                    "event_name": self.name,
                    "event_location": self.location,
                    "participant_location": participant.location,
                    "participant_locations": self.participant_locations,
                    "event_participants": self.num_participants,
                    "calculation": results
                }
            )
