import pyproj
from pydantic import BaseModel, conlist, confloat

from app.api.api_v1.calculator_interface import CalculatorInterface
from app.schemas.common import GeoCoordinates


class FlightStage(BaseModel):
    start: GeoCoordinates
    end: GeoCoordinates
    start_iso_code: str
    end_iso_code: str
    one_way: bool = True


class FlightStageCarbonSummary(BaseModel):
    stage: FlightStage
    distance: confloat(ge=0.0)
    carbon_kg: confloat(ge=0.0)


class FlightCalculatorRequest(BaseModel):
    stages: conlist(FlightStage, min_items=1)


class FlightCalculatorResponse(BaseModel):
    stages: list[FlightStageCarbonSummary]
    total_carbon_kg: confloat(ge=0.0)


def extend_flight_distance(distance: float) -> float:
    """Add factor to shortest flight distance to account for indirect flight paths

    Following https://www.icao.int/environmental-protection/CarbonOffset/Documents/Methodology%20ICAO%20Carbon%20Calculator_v11-2018.pdf
    section 4.2 we add a correction factor to represent deviations from the shortest
    path flown between points due to stacking, traffic and weather-driven corrections.

    Args:
        distance: Shortest distance - geodesic or Great Circle - between points in km

    Returns: Distance with additional correction factor
    """

    if distance < 550:
        return distance + 50
    elif distance < 5500:
        return distance + 100

    return distance + 125


def get_stage_distance(stage: FlightStage, geod: pyproj.Geod) -> float:
    """Calculate geodesic or great circle distances of flight stage

    Args:
        stage: Flight stage to calculate distance for
        geod: proj geodesic distance calculator

    Returns:
        Distance between stage start and end point, multiplied by two if return flight
    """
    start, end = stage.start, stage.end
    distance = geod.inv(start.lon, start.lat, end.lon, end.lat)[2] / 1000
    distance = extend_flight_distance(distance)
    return distance if stage.one_way else distance * 2


def lookup_carbon_intensity_kg(
    iso_code: str,
    default_intensity_grams: float = 89.0,
) -> float:
    """Find the carbon intensity in kg/km of a flight given the departure country

    Data sourced from Graver et al. ICCT Report: CO2 Emissions From Commercial
    Aviation: 2013, 2018, and 2019. (Table 4)

    See: https://theicct.org/publication/co2-emissions-from-commercial-aviation-2013-2018-and-2019

    Args:
        iso_code: Flight departure country
        default_intensity_grams: Default value departure countries not explicitly
            enumerated in paper

    Returns: CO2 intensity in kg/km flown of a flight originating from departure country
    """
    intensities = {
        "AE": 89,
        "AI": 87,
        "AS": 95,
        "AU": 90,
        "BM": 87,
        "CC": 90,
        "CN": 88,
        "CX": 90,
        "DE": 91,
        "ES": 79,
        "FK": 87,
        "FR": 87,
        "GB": 87,
        "GF": 87,
        "GG": 87,
        "GI": 87,
        "GP": 87,
        "GU": 95,
        "HK": 88,
        "IM": 87,
        "IN": 85,
        "JP": 95,
        "KY": 87,
        "MP": 95,
        "MQ": 87,
        "MS": 87,
        "NC": 87,
        "NF": 90,
        "PF": 87,
        "PM": 87,
        "PR": 95,
        "RE": 87,
        "SH": 87,
        "TC": 87,
        "UM": 95,
        "US": 95,
        "VG": 87,
        "VI": 95,
        "WF": 87,
        "YT": 87,
    }
    intensity_grams = intensities.get(iso_code, default_intensity_grams)
    return intensity_grams / 1000


def calculate_carbon_stage(
    stage: FlightStage,
    geod: pyproj.Geod,
    non_co2_effects_scaling: float = 1.9,
) -> FlightStageCarbonSummary:
    """Calculate flight emissions for an array of distances in km

    To account for the non-CO2 climate effects of aviation, the UK Government (in 2018)
    recommends applying a multiplier of 1.9:
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/726911/2018_methodology_paper_FINAL_v01-00.pdf

    A detailed scientific paper from 2010 on the climate effects of aviation supports an
    estimated multiplier of 1.9, but this excludes the effects of cirrus cloud
    formation, which is still not well understood:
    https://www.sciencedirect.com/science/article/pii/S1352231009004956

    Args:
        stage: Flight stage to calculate carbon intensity for
        geod: proj geodesic distance calculator
        non_co2_effects_scaling: Additional scaling for the non-CO2 climate effects of aviation

    Returns:
        Emitted CO2 in kg of each flight stage
    """
    distance = get_stage_distance(stage, geod)
    kg_co2_per_km = lookup_carbon_intensity_kg(stage.start_iso_code)
    carbon_kg = distance * kg_co2_per_km * non_co2_effects_scaling
    return FlightStageCarbonSummary(
        stage=stage,
        distance=distance,
        carbon_kg=carbon_kg,
    )


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


async def flight_calculator(
    request: FlightCalculatorRequest,
) -> FlightCalculatorResponse:
    """Calculate CO2 emissions for a series of flights"""
    stage_summaries = calculate_carbon_stages(request)
    response = build_response(stage_summaries)
    return response


calculator_interface = CalculatorInterface(
    name="flight_calculator",
    path="/flight",
    entrypoint=flight_calculator,
    request_model=FlightCalculatorRequest,
    response_model=FlightCalculatorResponse,
    get_total_carbon_kg=lambda response: response.total_carbon_kg,
)
