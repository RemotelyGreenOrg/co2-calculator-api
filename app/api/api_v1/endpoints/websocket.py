from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app import crud
from app.api import deps
from app.models import Event
from app.api.api_v1.endpoints.event_cost_aggregator import event_cost_aggregator


router = APIRouter()


def get_event(db: Session, event_id: str) -> Optional[Event]:
    event = crud.event.get(db=db, id=event_id)
    return event


def set_participant_active(db: Session, participant_id: str, is_active: bool) -> None:
    obj_in = {"active": is_active}
    crud.participant.find_and_update(db=db, id=participant_id, obj_in=obj_in)


async def update_sockets():
    results = await event_cost_aggregator()

    for participant in participants:
        if not participant.active:
            continue

        await participant.websocket.send_json(
            {
                "event_name": name,
                "event_location": location,
                "participant_location": participant.location,
                "participant_locations": participant_locations,
                "event_participants": num_participants,
                "calculation": results,
            }
        )


async def create_event(websocket, event_name, event_location, **data):
    event = events.get(event_name, None)
    if event is None:
        events[event_name] = event

    await websocket.send_json(
        {
            "event_name": event_name,
            "event_location": event_location,
            "event_participants": event.num_participants,
        }
    )


EventId = str
ParticipantId = str

websockets_table: dict[EventId, dict[ParticipantId, WebSocket]]


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(deps.get_db),
) -> None:
    """
    The websocket endpoint is listening at the root URL and is accessed via the
    Websocket protocol (ws or wss).
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            event_id = data.get("event_id")
            participant_id = data.get("participant_id")
            message = data.get("message")

            if not event_id or not participant_id:
                continue

            event = get_event(db, event_id)

            if event is None:
                continue

            participants = event.participants

            if message:
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
