from sqlite3 import connect
from fastapi import FastAPI
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from app.api import flight_calculator
from app.api import vc_calculator

# These default settings get overridden by environment variables.
# @see https://fastapi.tiangolo.com/advanced/settings/
class Settings(BaseSettings):
    host: str = "localhost:8000"


settings = Settings()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"message": "OK"}


all_connections = []
connections_by_event = []
# The websocket endpoint is listening at the root URL and is accessed via the Websocket protocol (ws or wss).


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    all_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "message" in data:
                for connection in all_connections:
                    await connection.send_json(data)
            if "event_name" in data:
                event_participants = 0
                for connection in connections_by_event:
                    if connection["event_name"] == data["event_name"]:
                        event_participants += 1
                print(event_participants)
                if event_participants == 0:
                    connections_by_event.append({"name": data["event_name"], "websocket": websocket})
                    await websocket.send_json({
                        "event_name": data["event_name"],
                        "event_location": data["event_location"],
                        "event_participants": event_participants
                    })
                elif event_participants > 1:
                    await websocket.send_json({
                        "event_name": data["event_name"],
                        "event_location": data["event_location"],
                        "event_participants": event_participants,
                        "calculation": 42 * event_participants
                    })

    except WebSocketDisconnect:
        all_connections.remove(websocket)
        for connection in connections_by_event:
            if connection["websocket"] == websocket:
                connections_by_event.remove(connection)


app.include_router(flight_calculator.router)
app.include_router(vc_calculator.router)
