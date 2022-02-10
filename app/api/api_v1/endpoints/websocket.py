from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app import crud, schemas
from app.api import deps
from app.api.api_v1.endpoints.event_cost_aggregator import (
    event_cost_aggregator,
    EventCostAggregatorRequest,
    EventCostAggregatorResponse,
)
from app.models import Event


EventId = int
ParticipantId = int
WebSocketTable = dict[EventId, dict[ParticipantId, WebSocket]]


def get_event(db: Session, event_id: int) -> Event:
    event = crud.event.get(db=db, id=event_id)
    return event


def set_participant_active(db: Session, participant_id: int, is_active: bool) -> None:
    obj_in = {"active": is_active}
    crud.participant.find_and_update(db=db, id=participant_id, obj_in=obj_in)


def update_event_and_participant_tables(
    db: Session,
    event_id: int,
    participant_id: int,
) -> Event:
    event = get_event(db, event_id)
    set_participant_active(db, participant_id, is_active=True)
    return event


async def publish_results(
    ws_table: WebSocketTable,
    event: schemas.Event,
    active_participants: list[schemas.Participant],
    results: EventCostAggregatorResponse,
) -> None:
    participant_websockets = ws_table[event.id]

    for participant in active_participants:
        websocket = participant_websockets[participant.id]
        await websocket.send_json(
            {
                "event": event.dict(),
                "participant": participant.dict(),
                "event_participants_count": len(active_participants),
                "calculation": results,
            }
        )


async def handle_socket(
    ws_table: WebSocketTable,
    websocket: WebSocket,
    event: Event,
    participant_id: int,
) -> WebSocketTable:
    active_participants = [p for p in event.participants if p.active]
    request = EventCostAggregatorRequest(event=event, participants=active_participants)
    results = await event_cost_aggregator(request)

    if event.id in ws_table:
        if participant_id not in ws_table[event.id]:
            ws_table[event.id][participant_id] = websocket
    else:
        ws_table[event.id] = {participant_id: websocket}

    await publish_results(ws_table, event, active_participants, results)

    return ws_table


router = APIRouter()
websockets_table: WebSocketTable = {}


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(deps.get_db),
) -> None:
    """
    The websocket endpoint is listening at the root URL and is accessed via the
    Websocket protocol (ws or wss).
    """
    participant_id = None

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            event_id = data.get("event_id")
            participant_id = data.get("participant_id")

            if not event_id or not participant_id:
                continue

            event = update_event_and_participant_tables(db, event_id, participant_id)
            websockets_table = await handle_socket(
                websockets_table,
                websocket,
                event,
                participant_id,
            )
    except WebSocketDisconnect:
        if participant_id:
            for participant_websockets in websockets_table.values():
                websocket = participant_websockets.get(participant_id)

                if websocket:
                    await websocket.close()
                    del participant_websockets[participant_id]

            set_participant_active(db, participant_id, is_active=False)
