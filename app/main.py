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
    websocket_endpoint: str = "ws://localhost:8000/footprint"


settings = Settings()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"message": "Hello world!"}


connections = []


@app.websocket("/footprint")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "message" in data:
                for connection in connections:
                    await connection.send_json(data)
    except WebSocketDisconnect:
        connections.remove(websocket)


@app.get("/footprint/settings")
def read_root():
    return {"websocket_endpoint": settings.websocket_endpoint}


app.include_router(flight_calculator.router)
app.include_router(vc_calculator.router)
