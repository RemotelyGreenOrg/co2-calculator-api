from typing import Any

import pyproj
from pydantic import BaseModel, conlist
from fastapi import APIRouter


router = APIRouter()


class Location(BaseModel):
    lon: float
    lat: float


class FlightStage(BaseModel):
    one_way: bool
    start: Location
    end: Location


class FlightCalculatorRequest(BaseModel):
    stages: conlist(FlightStage, min_items=1)


class FlightStageCarbonSummary(BaseModel):
    stage: FlightStage
    distance: float
    carbon_kg: float


class FlightCalculatorResponse(BaseModel):
    stages: list[FlightStageCarbonSummary]
    total_carbon_kg: float


def get_stage_distance(
    stage: FlightStage,
    geod: pyproj.Geod,
) -> float:
    """Calculate geodesic or great circle distances of flight stage

    Args:
        stage: Flight stage to calculate distance for
        geod: proj geodesic distance calculator

    Returns:
        Distance between stage start and end point, multiplied by two if return flight
    """
    start, end = stage.start, stage.end
    distance = geod.inv(start.lon, start.lat, end.lon, end.lat)[2] / 1000

    if stage.one_way:
        return distance

    return distance * 2


def calculate_carbon_stage(
    stage: FlightStage,
    geod: pyproj.Geod,
    carbon_intensity: float = 0.088,
    non_co2_effects_scaling: float = 1.9,
    flight_distance_scaling: float = 1.08,
) -> FlightStageCarbonSummary:
    """Calculate flight emissions for an array of distances in km

    The average carbon intensity from passenger aviation in 2018 was
    88g CO2/revenue-passenger-kilometer:
    https://theicct.org/sites/default/files/publications/ICCT_CO2-commercl-aviation-2018_20190918.pdf

    To account for the non-CO2 climate effects of aviation, the UK Government (in 2018)
    recommends applying a multiplier of 1.9:
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/726911/2018_methodology_paper_FINAL_v01-00.pdf

    A detailed scientific paper from 2010 on the climate effects of aviation supports an
    estimated multiplier of 1.9, but this excludes the effects of cirrus cloud
    formation, which is still not well understood:
    https://www.sciencedirect.com/science/article/pii/S1352231009004956

    The UK government (in 2018) recommends adding 8% to the great-circle distance to
    account for indirect flight paths and delays:
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/726911/2018_methodology_paper_FINAL_v01-00.pdf

    Args:
        stage: Flight stage to calculate carbon intensity for
        geod: proj geodesic distance calculator
        carbon_intensity: CO2 g/km flown
        non_co2_effects_scaling: Additional scaling for the non-CO2 climate effects of aviation
        flight_distance_scaling: Scale factor to account for indirect flight paths

    Returns:
        Emitted CO2 in kg of each flight stage
    """
    distance = get_stage_distance(stage, geod)
    kg_co2_per_km = carbon_intensity * non_co2_effects_scaling * flight_distance_scaling
    carbon_kg = distance * kg_co2_per_km
    return FlightStageCarbonSummary(stage=stage, distance=distance, carbon_kg=carbon_kg)


def calculate_carbon_stages(
    request: FlightCalculatorRequest,
    ellipse: str = "WGS84",
) -> list[FlightStageCarbonSummary]:
    """Calculate CO2 for all flight stages

    Args:
        request: Flight CO2 calculation request
        ellipse: Ellipsoid defining the  type of geodesic distance calculation

    Returns:
        List of summaries for CO2 emissions from each flight stage
    """
    geod = pyproj.Geod(ellps=ellipse)
    return [calculate_carbon_stage(stage, geod) for stage in request.stages]


def build_response(
    stage_summaries: list[FlightStageCarbonSummary],
) -> FlightCalculatorResponse:
    """Build API response"""
    total_carbon = sum(stage.carbon_kg for stage in stage_summaries)
    return FlightCalculatorResponse(
        stages=stage_summaries, total_carbon_kg=total_carbon
    )


@router.post("/flight", response_model=FlightCalculatorResponse)
def flight_calculator(request: FlightCalculatorRequest) -> FlightCalculatorResponse:
    """Calculate CO2 emissions for a series of flights"""
    stage_summaries = calculate_carbon_stages(request)
    response = build_response(stage_summaries)
    return response


def interface() -> list[dict[str, Any]]:
    return [request(), response()]


def request() -> dict[str, Any]:
    return FlightCalculatorRequest.schema()


def response() -> dict[str, Any]:
    return FlightCalculatorResponse.schema()
