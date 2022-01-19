from enum import Enum
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field, confloat

router = APIRouter()


class TrainType(str, Enum):
    TGV = "TGV"
    Intercity = "Intercity"
    TER = "TER"
    Transilien = "Transilien"
    Thalys = "Thalys"
    Eurostar = "Eurostar"
    Elipsos = "Elipsos"
    Gala = "Gala"
    Alleo = "Alleo"


class RailwayCompany(str, Enum):
    SNCF = "SNCF"
    SBB = "SBB/CFF/FFS"
    DB = "DB"


class TrainCalculatorRequest(BaseModel):
    """
    Request to the Train CO2 Calculator
    """

    distance: float = Field(
        42,
        title="Distance traveled",
        description="Distance traveled [km]",
        gt=0,
        lt=10000,
    )
    railway_company: RailwayCompany = Field(None, alias="Railway company")
    train_type: TrainType = Field(None, alias="Train type")

    class Config:
        title = "Train Calculator Request"


class TrainCalculatorResponse(BaseModel):
    """
    Response of the Train CO2 Calculator
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Train Calculator Response"


train_co2_list = [
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.TGV,
        "CO2 [g/km]": 3.2,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Intercity,
        "CO2 [g/km]": 11.8,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.TER,
        "CO2 [g/km]": 29.2,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Transilien,
        "CO2 [g/km]": 6.4,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Thalys,
        "CO2 [g/km]": 11.6,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Eurostar,
        "CO2 [g/km]": 11.2,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Elipsos,
        "CO2 [g/km]": 27,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Gala,
        "CO2 [g/km]": 12,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SNCF,
        "train type": TrainType.Alleo,
        "CO2 [g/km]": 11.3,
        "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
    },
    {
        "company": RailwayCompany.SBB,
        "CO2 [g/km]": 7,
        "source": "https://news.sbb.ch/artikel/89400/bye-bye-co2",
    },
]


def build_response(
    request: TrainCalculatorRequest,
) -> TrainCalculatorResponse:
    """Build API response"""
    co2_g_per_km = 10  # default average value
    for train in train_co2_list:
        if train["company"] == request.railway_company:
            if train["train type"] == request.train_type:
                co2_g_per_km = train["CO2 [g/km]"]
    total_carbon = co2_g_per_km / 1000 * request.distance
    return TrainCalculatorResponse(total_carbon_kg=total_carbon)


@router.post("/train", response_model=TrainCalculatorResponse)
def train_calculator(request: TrainCalculatorRequest) -> TrainCalculatorResponse:
    """Calculate CO2 emissions for a train trip"""
    response = build_response(request)
    return response


def interface() -> list[dict[str, Any]]:
    return [request(), response()]


def request() -> dict[str, Any]:
    return TrainCalculatorRequest.schema()


def response() -> dict[str, Any]:
    return TrainCalculatorResponse.schema()
