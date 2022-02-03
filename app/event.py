from dataclasses import dataclass
from typing import Optional, Union, Dict
from starlette.websockets import WebSocket
from pydantic import BaseModel
from .common import GeoCoordinates, JoinMode


UID = str


@dataclass
class ParticipantModel():
    location: GeoCoordinates
    join_mode: JoinMode
    websocket: WebSocket
    active: bool = True
    uid: Optional[UID] = None


class EventModelWebsocket():
    def __init__(self, name: str, location: Union[GeoCoordinates, str]):
        self.name = name
        self.location = location
        self.participants = {}

    @property
    def num_participants(self):
        return len(self.participants)

    @property
    def participant_locations(self):
        return [p.location for p in self.participants.values()]

    async def add_participant(self,
                              location: GeoCoordinates,
                              join_mode: JoinMode,
                              websocket: WebSocket,
                              # TODO: uid: str = None
                              ):
        #TODO: needs to be provided externally to have any meaning
        uid = str(self.num_participants)

        parti = self.participants.get(uid, None)
        if parti:
            parti.active = True
            parti.websocket = websocket
        else:
            parti = ParticipantModel(location, join_mode, websocket, True, uid)
            self.participants[uid] = parti

        await self.update_sockets()

    async def remove_participant(self, websocket: WebSocket):
        # TODO: This should work of UID not websockets...
        for participant in self.participants.values():
            if participant.websocket == websocket:
                participant.active = False
                participant.websocket = None

        await self.update_sockets()

    def compute_footprint(self):
        return 42 * self.num_participants

    async def update_sockets(self):
        results = self.compute_footprint()

        for participant in self.participants.values():
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
