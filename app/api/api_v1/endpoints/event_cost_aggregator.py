import asyncio
import itertools
from typing import cast, Final, Callable

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
from app.schemas.common import GeoCoordinates, JoinMode

router = APIRouter()


class EventCostAggregatorRequest(BaseModel):
    event: Event
    participants: list[Participant]


class EventCostAggregatorResponse(BaseModel):
    in_person_total_carbon_kg: float
    online_total_carbon_kg: float
    actual_total_carbon_kg: float
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
        title=JoinMode.in_person,
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
        title=JoinMode.online,
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


def merge_cost_aggregator_responses(request: EventCostAggregatorResponse, responses: list[CostAggregatorResponse]):
    def sum_cost_path_filter(select: Callable[[CostPath, Participant], bool]):
        cost_paths = itertools.chain.from_iterable(
            (
                (cp.total_carbon_kg for cp in response.cost_paths if select(cp, participant))
                for response, participant in zip(responses, request.participants)
            )
        )
        return sum(cost_paths)

    in_person_total = sum_cost_path_filter(lambda cp, _: cp.title == JoinMode.in_person)
    online_total = sum_cost_path_filter(lambda cp, _: cp.title == JoinMode.online)
    actual_total = sum_cost_path_filter(lambda cp, participant: cp.title == participant.join_mode)

    return EventCostAggregatorResponse(
        in_person_total_carbon_kg=in_person_total,
        online_total_carbon_kg=online_total,
        actual_total_carbon_kg=actual_total,
        participant_cost_aggregator_responses=responses,
    )


@router.post("/", response_model=EventCostAggregatorResponse)
async def event_cost_aggregator(
    request: EventCostAggregatorRequest,
) -> EventCostAggregatorResponse:
    requests = build_cost_aggregator_requests(request)
    response_futures = [cost_aggregator(req) for req in requests]
    responses = await asyncio.gather(*response_futures)
    responses = cast(list[CostAggregatorResponse], responses)
    response = merge_cost_aggregator_responses(request, responses)
    return response
