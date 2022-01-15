from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, confloat
from fastapi import APIRouter

router = APIRouter()


class FuelType(str, Enum):
    biodiesel = "Biodiesel"
    biogas = "Biogas"
    diesel = "Diesel"
    e10 = "E10 (Ethanol)"
    e85 = "E85 (Ethanol)"
    electric = "Electric"
    hybrid = "Hybrid"
    natruralgas = "Natural Gas"
    petrol = "Petrol"
    plugin = "Plugi-In Hybrid"


class CarType(str, Enum):
    compact = "Compact car"
    mid_range = "Mid-range car"
    luxury = "Luxury / SUV / Van"


class CarCalculatorRequest(BaseModel):
    """
    Request to the Car CO2 Calculator
    """

    distance: float = Field(
        42,
        title="Distance traveled",
        description="Distance traveled [km]",
        gt=0,
        lt=10000,
    )
    fuel_type: FuelType = Field(None, alias="Fuel type")
    car_type: CarType = Field(None, alias="Car type")
    taxi: bool = Field(...)
    consumption: float = Field(
        42,
        title="Fuel consumption",
        description="Car fuel consumption [l/100km]",
        gt=0,
        lt=50,
    )

    class Config:
        title = "Car Calculator Request"


class CarCalculatorResponse(BaseModel):
    """
    Response of the Car CO2 Calculator
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Car Calculator Response"


def build_response(
    request: CarCalculatorRequest,
) -> CarCalculatorResponse:
    """Build API response"""
    total_carbon = 0.205 * request.distance  # Private cars in France: 205 g of CO2/km
    return CarCalculatorResponse(total_carbon_kg=total_carbon)
    # https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey
    # source: Average use of private vehicles in France:
    # Sustainable Development and Energy Ministry - Observation and Statistics Department (SOeS)
    # Average consumption of passenger vehicles in France and fuel emissions factors:
    # ADEME – Carbon Base
    # Use of cars in km: 68% diesel and 32% petrol;
    # consumption: 6.6L/100 km for diesel and 7.8L/100 km for petrol;
    # emissions factors: 3.07 kg of CO2/L for diesel and 2.71 kg of CO2/L for petrol


@router.post("/car", response_model=CarCalculatorResponse)
def car_calculator(request: CarCalculatorRequest) -> CarCalculatorResponse:
    """Calculate CO2 emissions for a series of car trips"""
    response = build_response(request)
    return response


def interface() -> list[dict[str, Any]]:
    return [request(), response()]


def request() -> dict[str, Any]:
    return CarCalculatorRequest.schema()


def response() -> dict[str, Any]:
    return CarCalculatorResponse.schema()
