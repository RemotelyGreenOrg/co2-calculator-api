from enum import Enum
from typing import Optional, Final, Type

from pydantic import BaseModel, confloat, validator, Field

from app.api.api_v1.calculator_interface import CalculatorInterface


class ComparisonType(str, Enum):
    """Enumeration of available comparisons"""

    swiss_beef = "swiss_beef"
    swiss_captia = "swiss_captia"
    swiss_captia_grey = "swiss_captia_grey"
    swiss_tree = "swiss_tree"


class ComparisonConfig(BaseModel):
    """Configuration for CO2 comparison"""

    comparison_type: ComparisonType = Field(
        ..., description="Identifier for the type of comparison being made"
    )
    unit: str = Field(..., description="Quantity being compared against")
    co2_factor: confloat(ge=0.0) = Field(
        ..., description="Scale factor, 1 kg is equivalent to <co2_factor> units"
    )
    source: str = Field(..., description="Source for co2_factor")
    message_template: str = Field(
        ...,
        description=(
            "Unpopulated format string used to build CO2-equivalent message."
            "Must contain ' %f ' placeholder."
        ),
    )

    @validator("message_template")
    def validate_message_template(cls: Type["ComparisonConfig"], value: str) -> str:
        if " %f " not in value:
            raise ValueError("message_template must contain placeholder ' %f '")

        return value


class ComparisonResult(BaseModel):
    """Result of making CO2 comparison"""

    config: ComparisonConfig = Field(..., description="Configuration for comparison")
    co2_equivalent: confloat(ge=0.0) = Field(
        ..., description="Quantity of comparable items equivalent to given CO2 in kg"
    )
    co2_equivalent_message: str = Field(
        ..., description="Message summarizing CO2 equivalence"
    )


available_comparisons: Final[list[ComparisonConfig]] = [
    ComparisonConfig(
        comparison_type=ComparisonType.swiss_captia,
        unit="Swiss capita",
        # 6.4t CO2 produced per Swiss capita per year
        co2_factor=0.00015625,
        source="https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        message_template="the amount of CO2 caused by %f average Swiss people per year",
    ),
    ComparisonConfig(
        comparison_type=ComparisonType.swiss_captia_grey,
        unit="Swiss grey emissions capita",
        # 13.6t CO2 produced per Swiss capita per year
        co2_factor=0.0000735294,
        source="https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        message_template=(
            "the amount of CO2 caused by %f average Swiss people per year"
            " (including grey emmissions)"
        ),
    ),
    ComparisonConfig(
        comparison_type=ComparisonType.swiss_tree,
        unit="Swiss Tree",
        # 12.5kg CO2 bound per Swiss beech tree per year
        co2_factor=0.08,
        source="https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        message_template="the amount of CO2 %f average Swiss beech trees bind per year",
    ),
    ComparisonConfig(
        comparison_type=ComparisonType.swiss_beef,
        unit="Swiss Beef",
        # 80kg beef production creates 1t CO2
        co2_factor=0.08,
        source="https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        message_template=(
            "the amount of CO2 is caused by the production of %f kg Swiss beef"
        ),
    ),
]

available_comparisons_map: Final[dict[str, ComparisonConfig]] = {
    c.comparison_type: c for c in available_comparisons
}


def make_comparison(
    total_carbon_kg: float, comparison_type: ComparisonType
) -> ComparisonResult:
    """Find comparison config and use to calculate CO2-equivalent value

    Args:
        total_carbon_kg: Total CO2 in kg to make comparison with
        comparison_type: Type of comparison to make

    Returns: Result summarizing total CO2-equivalent in given units
    """
    config = available_comparisons_map[comparison_type]
    co2_equivalent = config.co2_factor * total_carbon_kg
    co2_equivalent_message = f"equivalent to {config.message_template % co2_equivalent}"
    return ComparisonResult(
        config=config,
        co2_equivalent=co2_equivalent,
        co2_equivalent_message=co2_equivalent_message,
    )


class ComparisonCalculatorRequest(BaseModel):
    """
    Request to the Comparison CO2 Calculator
    """

    total_carbon_kg: confloat(ge=0.0)
    comparison_types: Optional[list[ComparisonType]] = None

    class Config:
        title = "Comparison Calculator Request"


class ComparisonCalculatorResponse(BaseModel):
    """
    Response of the Comparison CO2 Calculator
    """

    comparisons: list[ComparisonResult]

    class Config:
        title = "Comparison Calculator Response"


def build_response(
    request: ComparisonCalculatorRequest,
) -> ComparisonCalculatorResponse:
    """Build API response"""
    requested_comparisons = request.comparison_types or [c for c in ComparisonType]
    comparisons = [
        make_comparison(request.total_carbon_kg, comparison_type)
        for comparison_type in requested_comparisons
    ]
    return ComparisonCalculatorResponse(comparisons=comparisons)


async def comparison_calculator(
    request: ComparisonCalculatorRequest,
) -> ComparisonCalculatorResponse:
    """Compare CO2 emissions to imaginable Comparisons"""
    response = build_response(request)
    return response


calculator_interface = CalculatorInterface(
    name="comparison_calculator",
    path="/comparison",
    entrypoint=comparison_calculator,
    request_model=ComparisonCalculatorRequest,
    response_model=ComparisonCalculatorResponse,
    get_total_carbon_kg=lambda _: 0,
)
