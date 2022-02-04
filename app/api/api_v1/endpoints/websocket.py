from fastapi import APIRouter
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.schemas.event import EventModelWebsocket

router = APIRouter()

all_connections = []
events = {}


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """
    The websocket endpoint is listening at the root URL and is accessed via the
    Websocket protocol (ws or wss).
    """
    await websocket.accept()
    all_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "message" in data:
                for connection in all_connections:
                    await connection.send_json(data)
            if "event_location" in data:
                await create_event(websocket, **data)
            if "participant_location" in data:
                await someone_joined_event(websocket, **data)

    except WebSocketDisconnect:
        for event in events.values():
            await event.remove_participant(websocket)
        all_connections.remove(websocket)


async def create_event(websocket, event_name, event_location, **data):
    event = events.get(event_name, None)
    if event is None:
        event = EventModelWebsocket(name=event_name, location=event_location)
        events[event_name] = event

    await websocket.send_json(
        {
            "event_name": event_name,
            "event_location": event_location,
            "event_participants": event.num_participants,
            # "participant_locations": event.participant_locations,
            # "calculation": 42 * event_participants,
        }
    )


async def someone_joined_event(websocket, event_name, **data):
    event = events[event_name]
    await event.add_participant(
        location=data["location"],
        # TODO: Pass through from front end
        join_mode="online",
        websocket=websocket,
    )
