from pydantic import BaseModel, confloat

from app.module_interface import ModuleInterface


class ComparisonItem(BaseModel):
    comparison: str
    value: confloat(ge=0.0)
    description: str


class ComparisonCalculatorRequest(BaseModel):
    """
    Request to the Comparison CO2 Calculator
    """

    total_carbon_kg: confloat(ge=0.0)

    class Config:
        title = "Template Module Request"


class ComparisonCalculatorResponse(BaseModel):
    """
    Response of the Comparison CO2 Calculator
    """

    comparisons: list[ComparisonItem]

    class Config:
        title = "Comparison Calculator Response"


# description: /X replaces a number;
# descriptions should start continuing the sentence: "This is equivalent to "...
comparison_co2_list = [
    {
        "comparison": "Swiss capita equivalent",
        "co2 factor [1/kg]": 0.00015625,  # 6.4t CO2 produced per Swiss capita per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "description": "how much CO2 /X averge Swiss person cause per year.",
    },
    {
        "comparison": "Swiss grey emmisions capita equivalent",
        "co2 factor [1/kg]": 0.0000735294,  # 13.6t CO2 produced per Swiss capita per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "description": "how much CO2 /X averge Swiss person (including grey emmissions) cause per year.",
    },
    {
        "comparison": "Swiss Tree equivalent",
        "co2 factor [1/kg]": 0.08,  # 12.5kg CO2 bound per Swiss beech tree per year
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "description": "how much CO2 /X averge Swiss beech trees bind per year.",
    },
    {
        "comparison": "Swiss Beef equivalent",
        "co2 factor [1/kg]": 0.08,  # 80kg beef production creates 1t CO2
        "source": "https://www.oekoservice.ch/images/news/2016/Factsheet_Swiss_Climate_Wie_viel_ist_eine_Tonne_CO2.pdf",
        "description": "how much CO2 is caused by the production of /X kg Swiss beef.",
    },
]


def build_response(
    request: ComparisonCalculatorRequest,
) -> ComparisonCalculatorResponse:
    """Build API response"""
    results = []
    for comparison in comparison_co2_list:
        value = request.total_carbon_kg * comparison["co2 factor [1/kg]"]
        comparison_item = {
            "comparison": comparison["comparison"],
            "value": value,
            "description": "This is equivalent to "
            + comparison["description"].replace("/X", str(value)),
        }
        results.append(comparison_item)
    return ComparisonCalculatorResponse(comparisons=results)


async def comparison_calculator(
    request: ComparisonCalculatorRequest,
) -> ComparisonCalculatorResponse:
    """Compare CO2 emissions to imaginable Comparisons"""
    response = build_response(request)
    return response


module = ModuleInterface(
    name="comparison_calculator",
    path="/comparison",
    entrypoint=comparison_calculator,
    request_model=ComparisonCalculatorRequest,
    response_model=ComparisonCalculatorResponse,
    get_total_carbon_kg=lambda _: 0,
)
