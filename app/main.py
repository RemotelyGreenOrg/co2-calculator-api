from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from . import cost_aggregator
from .modules import modules
from .event import EventModelWebsocket


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
events = {}
connections_by_event = []


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """
    The websocket endpoint is listening at the root URL and is accessed via the
    Websocket protocol (ws or wss).
    """
    await websocket.accept()
    print("BEK", websocket)
    print("BEK", websocket.headers)
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
        all_connections.remove(websocket)
        for event in events.values():
            await event.remove_participant(websocket)

        for connection in connections_by_event:
            if connection["websocket"] == websocket:
                connections_by_event.remove(connection)


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
            #"participant_locations": event.participant_locations,
            #"calculation": 42 * event_participants,
        })


async def someone_joined_event(websocket, event_name, **data):
    event = events[event_name]
    await event.add_participant(location=data["location"],
                                #TODO: Pass through from front end
                                join_mode="online", 
                                websocket=websocket,
                                )



# ==================================================================
# Register modules and routers
modules.register(app)
app.include_router(cost_aggregator.router)
# ==================================================================
