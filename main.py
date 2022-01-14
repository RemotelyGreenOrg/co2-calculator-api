from fastapi import FastAPI
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from vc_calculator.interface import make_device, OnlineDetails, compute
import vc_calculator.interface as online


# These default settings get overridden by environment variables. @see https://fastapi.tiangolo.com/advanced/settings/
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


@app.post("/online")
def calculate(body: online.OnlineDetails):
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results
