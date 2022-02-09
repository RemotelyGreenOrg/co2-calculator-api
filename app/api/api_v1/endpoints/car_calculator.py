from enum import Enum

from pydantic import BaseModel, Field, confloat

from app.api.api_v1.calculator_interface import CalculatorInterface


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
    plugin = "Plug-In Hybrid"


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
    """Build API response

    Sources:
        https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey

        Average use of private vehicles in France: Sustainable Development and Energy
        Ministry - Observation and Statistics Department (SOeS)

        Average consumption of passenger vehicles in France and fuel emissions factors:
        ADEME – Carbon Base

    Private cars in France: 205 g of CO2/km
    Use of cars in km: 68% diesel and 32% petrol;
    Consumption: 6.6L/100 km for diesel and 7.8L/100 km for petrol;
    Emissions factors: 3.07 kg of CO2/L for diesel and 2.71 kg of CO2/L for petrol
    """
    car_co2_kg_per_km = 0.205
    total_carbon = car_co2_kg_per_km * request.distance
    return CarCalculatorResponse(total_carbon_kg=total_carbon)


async def car_calculator(request: CarCalculatorRequest) -> CarCalculatorResponse:
    """Calculate CO2 emissions for a car trips"""
    response = build_response(request)
    return response


module = CalculatorInterface(
    name="car_calculator",
    path="/car",
    entrypoint=car_calculator,
    request_model=CarCalculatorRequest,
    response_model=CarCalculatorResponse,
    get_total_carbon_kg=lambda response: response.total_carbon_kg,
)
