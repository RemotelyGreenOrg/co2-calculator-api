from enum import Enum

from pydantic import BaseModel, Field, confloat

from app.api.api_v1.calculator_interface import CalculatorInterface


class TrainType(str, Enum):
    Alleo = "Alleo"
    Elipsos = "Elipsos"
    Eurostar = "Eurostar"
    Gala = "Gala"
    Intercity = "Intercity"
    TER = "TER"
    TGV = "TGV"
    Thalys = "Thalys"
    Transilien = "Transilien"
    Unknown = "Unknown"


class RailwayCompany(str, Enum):
    DB = "DB"
    SBB = "SBB/CFF/FFS"
    SNCF = "SNCF"


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


def lookup_carbon_intensity_grams(
    request: TrainCalculatorRequest,
    default_co2_g_per_km: float = 10.0,
) -> float:
    carbon_intensities = {
        RailwayCompany.SBB: {
            TrainType.Unknown: {
                "CO2 [g/km]": 7.0,
                "source": "https://news.sbb.ch/artikel/89400/bye-bye-co2",
            }
        },
        RailwayCompany.SNCF: {
            TrainType.Alleo: {
                "CO2 [g/km]": 11.3,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Elipsos: {
                "CO2 [g/km]": 27.0,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Eurostar: {
                "CO2 [g/km]": 11.2,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Gala: {
                "CO2 [g/km]": 12.0,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Intercity: {
                "CO2 [g/km]": 11.8,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.TER: {
                "CO2 [g/km]": 29.2,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.TGV: {
                "CO2 [g/km]": 3.2,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Thalys: {
                "CO2 [g/km]": 11.6,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
            TrainType.Transilien: {
                "CO2 [g/km]": 6.4,
                "source": "https://ch.oui.sncf/en/help-ch/calculation-co2-emissions-your-train-journey",
            },
        },
    }
    train_details = carbon_intensities.get(request.railway_company, {}).get(
        request.train_type, {}
    )
    return train_details.get("CO2 [g/km]", default_co2_g_per_km)


def build_response(request: TrainCalculatorRequest) -> TrainCalculatorResponse:
    """Build API response"""
    co2_g_per_km = lookup_carbon_intensity_grams(request)
    total_carbon_kg = co2_g_per_km / 1000 * request.distance
    return TrainCalculatorResponse(total_carbon_kg=total_carbon_kg)


def train_calculator(request: TrainCalculatorRequest) -> TrainCalculatorResponse:
    """Calculate CO2 emissions for a train trip"""
    response = build_response(request)
    return response


module = CalculatorInterface(
    name="train_calculator",
    path="/train",
    entrypoint=train_calculator,
    request_model=TrainCalculatorRequest,
    response_model=TrainCalculatorResponse,
    get_total_carbon_kg=lambda response: response.total_carbon_kg,
)
