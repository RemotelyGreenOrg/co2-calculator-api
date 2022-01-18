from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, confloat
from fastapi import APIRouter

router = APIRouter()


class ComperisonItem(BaseModel):
    comparison: str
    value: confloat(ge=0.0)
    description: str


class ComperisonCalculatorRequest(BaseModel):
    """
    Request to the Comparison CO2 Calculator
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Template Module Request"


class ComperisonCalculatorResponse(BaseModel):
    """
    Response of the Comparison CO2 Calculator
    """

    comparisons: list[ComperisonItem]

    class Config:
        title = "Comparison Calculator Response"


# description: /X replaces a number;
# decriptions should start continuing the sentence: "This is equivalent to "...
comparison_co2_list = [
    {
        "comparison": "Swiss capita equivalent",
        "co2 factor [1/kg]": 0.00015625,  # 6.4t CO2 produced per Swiss capita per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "decription": "how much CO2 /X averge Swiss person cause per year.",
    },
    {
        "comparison": "Swiss grey emmisions capita equivalent",
        "co2 factor [1/kg]": 0.0000735294,  # 13.6t CO2 produced per Swiss capita per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "decription": "how much CO2 /X averge Swiss person (including grey emmissions) cause per year.",
    },
    {
        "comparison": "Swiss Tree equivalent",
        "co2 factor [1/kg]": 0.08,  # 12.5kg CO2 bound per Swiss beech tree per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "decription": "how much CO2 /X averge Swiss beech trees bind per year.",
    },
    {
        "comparison": "Swiss Beef equivalent",
        "co2 factor [1/kg]": 0.08,  # 80kg beef production creates 1t CO2
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "decription": "how much CO2 is caused by the production of /X kg Swiss beef.",
    },
]


def build_response(
    request: ComperisonCalculatorRequest,
) -> ComperisonCalculatorResponse:
    """Build API response"""
    results = []
    for comparison in comparison_co2_list:
        value = request.total_carbon_kg * comparison["co2 factor [1/kg]"]
        comperison_item = {
            "comparison": comparison["comparison"],
            "value": value,
            "description": "This is equivalent to "
            + comparison["decription"].replace("/X", str(value)),
        }
        results.append(comperison_item)
    return ComperisonCalculatorResponse(comparisons=results)


@router.post("/comparison", response_model=ComperisonCalculatorResponse)
def comparison_calculator(
    request: ComperisonCalculatorRequest,
) -> ComperisonCalculatorResponse:
    """Compare CO2 emissions to imaginable Comparisons"""
    response = build_response(request)
    return response


def interface() -> list[dict[str, Any]]:
    return [request(), response()]


def request() -> dict[str, Any]:
    return ComperisonCalculatorRequest.schema()


def response() -> dict[str, Any]:
    return ComperisonCalculatorResponse.schema()
