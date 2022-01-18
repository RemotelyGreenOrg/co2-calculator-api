from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

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
# Modules


@app.get("/modules")
async def get() -> dict[str, list[dict[str, Any]]]:
    return {"modules": modules.interfaces}


@app.get("/requests")
async def get() -> dict[str, list[dict[str, Any]]]:
    return {"requests": modules.request_schemas}


@app.get("/responses")
async def get() -> dict[str, list[dict[str, Any]]]:
    return {"responses": modules.response_schemas}


# Register modules
modules.include_routers(app)
# ==================================================================
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
            # Looking for the module with this return type
            for module in module_list:
                if cost_item.module == module.request()["title"]:
                    # Calling the code that computes the information
                    # Todo: extend and use module interface
                    if cost_item.module == "OnlineDetails":
                        from app.api.vc_calculator import online_calculator
                        from vc_calculator.interface import OnlineDetails
                        res = online_calculator(
                            OnlineDetails(**cost_item.properties))
                        import statistics
                        total_carbon_kg += statistics.mean(
                            [res.total_emissions.low, res.total_emissions.high])
                    elif cost_item.module == "FlightCalculatorRequest":
                        from app.api.flight_calculator import flight_calculator, FlightCalculatorRequest
                        res = flight_calculator(
                            FlightCalculatorRequest(**cost_item.properties))
                        total_carbon_kg += res.total_carbon_kg
            cost_items.append( CostItemResponse(cost_item = cost_item) )
        cost_paths.append( CostPathResponse(cost_items = cost_items, title = cost_path.title, total_carbon_kg = total_carbon_kg) )
    return CostAggregatorResponse(cost_paths = cost_paths)
    #return {"message": "OK"}

# Include the module routers
for module in module_list:
    app.include_router(module.router)
