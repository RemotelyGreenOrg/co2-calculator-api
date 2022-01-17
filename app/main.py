from fastapi import FastAPI
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

# MODULES:
from importlib import import_module

module_import_list = [
#    "app.api.template_module",
#    "app.api.another_module",
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
                connections_by_event.append({"name": data["event_name"], "websocket": websocket})
                await websocket.send_json({
                    "event_name": data["event_name"],
                    "event_location": data["event_location"],
                    # send back an initial calculation if available
                    "calculation": 42
                })

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


# Fucntions to call for each module are hard-coded for now
# Todo: use interface to obtain function to call for each module
# Todo: perform input sanity check and handle module errors per module
# Todo: move into own module

from pydantic import BaseModel, conlist, confloat
from typing import Any

class CostItem(BaseModel):
    module: str
    properties: Any

class CostPath(BaseModel):
    title: str
    cost_items: conlist(CostItem, min_items=1)

class CostAggregatorRequest(BaseModel):
    cost_paths: conlist(CostPath, min_items=1)

class CostItemResponse(BaseModel):
    cost_item: CostItem

class CostPathResponse(BaseModel):
    title: str
    total_carbon_kg: confloat(ge=0.0)
    cost_items: conlist(CostItemResponse)

class CostAggregatorResponse(BaseModel):
    cost_paths: conlist(CostPathResponse)

@app.post("/cost_aggregator")
async def cost_aggregator(request: CostAggregatorRequest) -> CostAggregatorResponse:
    cost_paths = []
    for cost_path in request.cost_paths:
        cost_items = []
        total_carbon_kg = 0.0
        for cost_item in cost_path.cost_items:
            print(cost_item.module)
            # Looking for the module with this return type
            for module in module_list:
                print(module.request()["title"])
                if cost_item.module == module.request()["title"]:
                    print("Found it")
                    # Calling the code that computes the information
                    # Todo: extend and use module interface
                    if cost_item.module == "OnlineDetails":
                        print("Hello")
                        print(cost_item.properties)
                        from app.api.vc_calculator import online_calculator
                        from vc_calculator.interface import OnlineDetails
                        res = online_calculator(
                            OnlineDetails(**cost_item.properties))
                        import statistics
                        total_carbon_kg += statistics.mean(
                            [res.total_emissions.low, res.total_emissions.high])
                        print(res)
                    elif cost_item.module == "FlightCalculatorRequest":
                        from app.api.flight_calculator import flight_calculator, FlightCalculatorRequest
                        res = flight_calculator(
                            FlightCalculatorRequest(**cost_item.properties))
                        total_carbon_kg += res.total_carbon_kg
                        print(res)
            cost_items.append( CostItemResponse(cost_item = cost_item) )
        cost_paths.append( CostPathResponse(cost_items = cost_items, title = cost_path.title, total_carbon_kg = total_carbon_kg) )
    return CostAggregatorResponse(cost_paths = cost_paths)
    #return {"message": "OK"}

# Include the module routers
for module in module_list:
    app.include_router(module.router)
