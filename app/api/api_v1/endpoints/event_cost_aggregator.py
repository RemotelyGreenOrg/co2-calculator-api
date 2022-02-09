import asyncio

from fastapi import APIRouter
from vc_calculator.interface import OnlineDetails

from app.api.api_v1.endpoints.cost_aggregator import (
    cost_aggregator,
    CostAggregatorRequest,
    CostPath,
    CostItem,
)
from app.api.api_v1.endpoints import flight_calculator
from app.api.api_v1.endpoints import online_calculator as online
from app.api.api_v1.endpoints.flight_calculator import (
    FlightCalculatorRequest,
    FlightStage,
)
from app.schemas.common import GeoCoordinates


def build_in_person_cost_path(participant, end: GeoCoordinates) -> CostPath:
    location = participant.location
    start = GeoCoordinates(lon=location["longitude"], lat=location["latitude"])
    flight_stage = FlightStage(start=start, end=end, one_way=False)
    in_person_path = CostPath(
        title="In Person Attendance",
        cost_items=[
            CostItem(
                module=flight_calculator.module.name,
                propertices=FlightCalculatorRequest(stages=[flight_stage]).dict(),
            )
        ],
    )
    return in_person_path


def build_online_cost_path(event):
    details = OnlineDetails(
        location=None,  # str,
        device_list=None,  # List[Union[HardwareDetails, KnownDevicesEnum]],
        bandwidth=None,  # float,
        total_participants=None,  # int,
        software=None,  # Optional[str],
        connection=None,  # Optional[ConnectionTypes],
    )
    online_path = CostPath(
        title="Online Attendance",
        cost_items=[CostItem(module=online.module.name, propertices=details.dict())],
    )
    return online_path


def build_cost_aggregator_request(
    participant, end: GeoCoordinates
) -> CostAggregatorRequest:
    location = participant.location
    in_person_path = build_in_person_cost_path(location, end)
    online_path = build_online_cost_path(participant)
    return CostAggregatorRequest(cost_paths=[in_person_path, online_path])


def build_cost_aggregator_requests(event) -> list[CostAggregatorRequest]:
    location = event.location
    end = GeoCoordinates(lon=location["longitude"], lat=location["latitude"])
    participants = event.participants
    requests = [
        build_cost_aggregator_request(participant, end) for participant in participants
    ]
    return requests


def merge_cost_aggregator_responses(responses):
    return {"blah": 10}


router = APIRouter()


@router.post("/event-cost-aggregator")
async def event_cost_aggregator(event):
    requests = build_cost_aggregator_requests(event)
    responses = [cost_aggregator(request) for request in requests]
    responses = await asyncio.gather(*responses)
    response = merge_cost_aggregator_responses(responses)
    return response
