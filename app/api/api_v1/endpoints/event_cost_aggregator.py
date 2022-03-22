import asyncio
import itertools
from typing import cast, Final

import reverse_geocoder
from fastapi import APIRouter
from pydantic import BaseModel
from vc_calculator.interface import OnlineDetails, ConnectionTypes, KnownDevicesEnum

from app.api.api_v1.endpoints import flight_calculator
from app.api.api_v1.endpoints import online_calculator as online
from app.api.api_v1.endpoints.cost_aggregator import (
    cost_aggregator,
    CostAggregatorRequest,
    CostPath,
    CostItem,
    CostAggregatorResponse,
)
from app.api.api_v1.endpoints.flight_calculator import (
    FlightCalculatorRequest,
    FlightStage,
)
from app.schemas import Event, Participant
from app.schemas.common import GeoCoordinates

router = APIRouter()


IN_PERSON_ATTENDANCE_TITLE: Final[str] = "In-Person Attendance"
ONLINE_ATTENDANCE_TITLE: Final[str] = "Online Attendance"


class EventCostAggregatorRequest(BaseModel):
    event: Event
    participants: list[Participant]


class EventCostAggregatorResponse(BaseModel):
    in_person_total_carbon_kg: float
    online_total_carbon_kg: float
    participant_cost_aggregator_responses: list[CostAggregatorResponse]


def build_in_person_cost_path(
    participant: Participant,
    end: GeoCoordinates,
) -> CostPath:
    start = GeoCoordinates(lon=participant.lon, lat=participant.lat)

    coordinates = [(start.lat, start.lon), (end.lat, end.lon)]
    results = reverse_geocoder.search(coordinates)[:2]
    flight_stage = FlightStage(start=start, end=end,
                               start_iso_code=results[0]["cc"],
                               end_iso_code=results[1]["cc"], one_way=False)
    in_person_path = CostPath(
        title=IN_PERSON_ATTENDANCE_TITLE,
        cost_items=[
            CostItem(
                calculator_name=flight_calculator.calculator_interface.name,
                request=FlightCalculatorRequest(stages=[flight_stage]).dict(),
            )
        ],
    )
    return in_person_path


def build_online_cost_path(total_participants: int) -> CostPath:
    details = OnlineDetails(
        location="home",
        device_list=[KnownDevicesEnum.pc],
        bandwidth=5,
        total_participants=total_participants,
        software="linux",
        connection=ConnectionTypes.wifi,
    )
    online_path = CostPath(
        title=ONLINE_ATTENDANCE_TITLE,
        cost_items=[
            CostItem(
                calculator_name=online.calculator_interface.name,
                request=details.dict(),
            )
        ],
    )
    return online_path


def build_cost_aggregator_request(
    participant: Participant,
    end: GeoCoordinates,
    total_participants: int,
) -> CostAggregatorRequest:
    in_person_path = build_in_person_cost_path(participant, end)
    online_path = build_online_cost_path(total_participants)
    return CostAggregatorRequest(cost_paths=[in_person_path, online_path])


def build_cost_aggregator_requests(
    request: EventCostAggregatorRequest,
) -> list[CostAggregatorRequest]:
    event = request.event
    participants = request.participants
    end = GeoCoordinates(lon=event.lon, lat=event.lat)
    total_participants = len(participants)
    requests = [
        build_cost_aggregator_request(participant, end, total_participants)
        for participant in participants
    ]
    return requests


def merge_cost_aggregator_responses(responses: list[CostAggregatorResponse]):
    in_person_results = itertools.chain.from_iterable(
        [
            [cp for cp in response.cost_paths if cp.title == IN_PERSON_ATTENDANCE_TITLE]
            for response in responses
        ]
    )
    online_results = itertools.chain.from_iterable(
        [
            [cp for cp in response.cost_paths if cp.title == ONLINE_ATTENDANCE_TITLE]
            for response in responses
        ]
    )

    in_person_total = sum(result.total_carbon_kg for result in in_person_results)
    online_total = sum(result.total_carbon_kg for result in online_results)

    return EventCostAggregatorResponse(
        in_person_total_carbon_kg=in_person_total,
        online_total_carbon_kg=online_total,
        participant_cost_aggregator_responses=responses,
    )


@router.post("/", response_model=EventCostAggregatorResponse)
async def event_cost_aggregator(
    request: EventCostAggregatorRequest,
) -> EventCostAggregatorResponse:
    requests = build_cost_aggregator_requests(request)
    response_futures = [cost_aggregator(request) for request in requests]
    responses = await asyncio.gather(*response_futures)
    responses = cast(list[CostAggregatorResponse], responses)
    response = merge_cost_aggregator_responses(responses)
    return response
