from fastapi import FastAPI
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

# MODULES:
from importlib import import_module

module_import_list = [
    "app.api.template_module",
    "app.api.another_module",
    "app.api.flight_calculator",
    "app.api.vc_calculator",
]
module_list = []
for module in module_import_list:
    module_list.append(import_module(module, __name__))


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

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    # The websocket endpoint is listening at the root URL and is accessed via the
    # Websocket protocol (ws or wss).
    await websocket.accept()
    all_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "message" in data:
                for connection in all_connections:
                    await connection.send_json(data)
            if "event_name" in data:
                connections_by_event.append(
                    {"name": data["event_name"], "websocket": websocket}
                )
                # send back an initial calculation if available
                await websocket.send_json(
                    {"event_name": data["event_name"], "calculation": 1}
                )

    except WebSocketDisconnect:
        all_connections.remove(websocket)
        for connection in connections_by_event:
            if connection["websocket"] == websocket:
                connections_by_event.remove(connection)


@app.get("/modules")
async def get():
    interfaces = []
    for module in module_list:
        for req_res in module.interface():  # interface has request and response
            interfaces.append(req_res)
    module_json = {"modules": interfaces}
    return module_json


@app.get("/requests")
async def get():
    requests = []
    for module in module_list:
        requests.append(module.request())
    module_json = {"requests": requests}
    return module_json


@app.get("/responses")
async def get():
    responses = []
    for module in module_list:
        responses.append(module.response())
    module_json = {"responses": responses}
    return module_json


# Include the module routers
for module in module_list:
    app.include_router(module.router)
