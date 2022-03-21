from typing import Optional, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app import crud, schemas, models
from app.api import deps
from app.api.api_v1.endpoints.event_cost_aggregator import (
    event_cost_aggregator,
    EventCostAggregatorRequest,
    EventCostAggregatorResponse,
)


EventId = int
ParticipantId = int


class WebSocketTable:
    def __init__(self: "WebSocketTable") -> None:
        self._table: dict[EventId, dict[ParticipantId, WebSocket]] = {}

    def __call__(self: "WebSocketTable") -> "WebSocketTable":
        return self

    @property
    def table(self: "WebSocketTable") -> dict[EventId, dict[ParticipantId, WebSocket]]:
        return self._table

    def get_participant_websocket(
        self: "WebSocketTable",
        event_id: EventId,
        participant_id: ParticipantId,
    ) -> Optional[WebSocket]:
        event_id = EventId(event_id) # Seems to need explicit casting

        participant_sockets = self.table.get(event_id)

        if participant_sockets is not None:
            return participant_sockets.get(participant_id)

        return None

    def add_participant_websocket(
        self: "WebSocketTable",
        event_id: EventId,
        participant_id: ParticipantId,
        websocket: WebSocket,
    ) -> "WebSocketTable":
        event_id = EventId(event_id) # Seems to need explicit casting
        if event_id not in self.table:
            self.table[event_id] = {participant_id: websocket}

        elif participant_id not in self.table[event_id]:
            self.table[event_id][participant_id] = websocket

        return self

    def remove_participant_websocket(
        self: "WebSocketTable",
        event_id: EventId,
        participant_id: ParticipantId,
    ) -> Optional[WebSocket]:
        event_id = EventId(event_id) # Seems to need explicit casting
        socket = self.table.get(event_id, {}).get(participant_id)

        if socket is not None:
            del self.table[event_id][participant_id]

        return socket

    async def send_json_to_event_participant(
        self: "WebSocketTable",
        event_id: EventId,
        participant_id: ParticipantId,
        data: dict[str, Any],
    ) -> None:
        event_id = EventId(event_id) # Seems to need explicit casting

        participant_socket = self.get_participant_websocket(event_id, participant_id)
        if participant_socket is not None:
            await participant_socket.send_json(data)

    def participant_connection_closed(
        self: "WebSocketTable",
        event_id: Optional[int],
        participant_id: Optional[int],
    ) -> None:
        event_id = EventId(event_id) # Seems to need explicit casting

        if event_id and participant_id:
            websocket = self.remove_participant_websocket(event_id, participant_id)


def _get_event(db: Session, event_id: int) -> schemas.Event:
    db_event = crud.event.get(db=db, id=event_id)
    event = schemas.Event.from_orm(db_event)
    return event


def _set_participant_active(db: Session, participant_id: int, is_active: bool) -> None:
    obj_in = {"active": is_active}
    crud.participant.find_and_update(db=db, id=participant_id, obj_in=obj_in)


def _update_event_and_participant_tables(
    db: Session,
    event_id: int,
    participant_id: int,
) -> models.Event:
    _set_participant_active(db, participant_id, is_active=True)
    event = _get_event(db, event_id)
    return event


async def _publish_event_costs(
    ws_table: WebSocketTable,
    event: schemas.Event,
    active_participants: list[schemas.Participant],
    costs: EventCostAggregatorResponse,
) -> None:
    event_participants_count = len(active_participants)

    for participant in active_participants:
        data = {
            "event": event.dict(),
            "participant": participant.dict(),
            "event_participants_count": event_participants_count,
            "calculation": costs.dict(),
        }
        await ws_table.send_json_to_event_participant(event.id, participant.id, data)


async def _recalculate_event_costs(
    event: models.Event,
    active_participants: list[models.Participant],
) -> EventCostAggregatorResponse:
    request = EventCostAggregatorRequest(event=event, participants=active_participants)
    results = await event_cost_aggregator(request)
    return results


router = APIRouter()
websockets_table = WebSocketTable()


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    ws_table: WebSocketTable = Depends(websockets_table),
    db: Session = Depends(deps.get_db),
) -> None:
    """
    The websocket endpoint is listening at the root URL and is accessed via the
    Websocket protocol (ws or wss).
    """
    event_id = None
    participant_id = None

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            event_id = data.get("event_id")
            participant_id = data.get("participant_id")

            if not event_id or not participant_id:
                continue

            ws_table = ws_table.add_participant_websocket(event_id, participant_id, websocket)
            event = _update_event_and_participant_tables(db, event_id, participant_id)
            active_participants = [p for p in event.participants if p.active]
            costs = await _recalculate_event_costs(event, active_participants)
            await _publish_event_costs(ws_table, event, active_participants, costs)
    except WebSocketDisconnect:
        if participant_id:
            ws_table.participant_connection_closed(event_id, participant_id)
            _set_participant_active(db, participant_id, is_active=False)
