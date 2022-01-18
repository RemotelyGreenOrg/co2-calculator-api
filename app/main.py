from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.api import cost_aggregator
from app.api.modules import modules


class Settings(BaseSettings):
    """Default settings for app

    These default settings get overridden by environment variables.
    @see https://fastapi.tiangolo.com/advanced/settings/
    """

    host: str = "localhost:8000"


settings = Settings()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"message": "OK"}


all_connections = []
connections_by_event = []


@app.websocket("/")
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
            if "event_name" in data:

                event_name = data["event_name"]
                connections_by_event.append(
                    {
                        "event_name": data["event_name"],
                        "data": data,
                        "websocket": websocket,
                    }
                )

                connections_for_this_event = [
                    c for c in connections_by_event if c["event_name"] == event_name
                ]
                event_participants = len(connections_by_event)
                participant_locations = [
                    (c["data"]["latitude"], c["data"]["longitude"])
                    for c in connections_for_this_event
                    if "participant_location" in c["data"]
                ]

                if event_participants == 1:
                    await websocket.send_json(
                        {
                            "event_name": data["event_name"],
                            "event_location": data["event_location"],
                            "event_participants": 0,
                            "participant_locations": participant_locations,
                            "calculation": 42 * event_participants,
                        }
                    )
                elif event_participants > 1:
                    # TODO add event_location
                    for c in connections_by_event:
                        await c["websocket"].send_json(

                                {
                            "event_name": data["event_name"],
                            "participant_location": data["participant_location"],
                                "participant_locations": participant_locations,
                            "event_participants": event_participants,
                            "calculation": 42 * event_participants,
                        }
                    )

    except WebSocketDisconnect:
        all_connections.remove(websocket)
        for connection in connections_by_event:
            if connection["websocket"] == websocket:
                connections_by_event.remove(connection)


# ==================================================================
# Register modules and routers
modules.register(app)
app.include_router(cost_aggregator.router)
# ==================================================================
