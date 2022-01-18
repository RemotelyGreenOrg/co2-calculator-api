import statistics

import vc_calculator.interface as online

from app.api.module_interface import ModuleInterface


async def online_calculator(
    body: online.OnlineDetails,
) -> online.OnlineCalculatorResponse:
    """Calculate CO2 emissions for an online video call"""
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results


def get_total_carbon_kg(response: online.OnlineCalculatorResponse) -> float:
    emissions = response.total_emissions
    return statistics.mean([emissions.low, emissions.high])


module = ModuleInterface(
    name="online_calculator",
    path="/online",
    entrypoint=online_calculator,
    request_model=online.OnlineDetails,
    response_model=online.OnlineCalculatorResponse,
    get_total_carbon_kg=get_total_carbon_kg,
)
