import vc_calculator.interface as online
from fastapi import APIRouter

from app.api.module_interface import ModuleInterface

router = APIRouter()


@router.post("/online")
def online_calculator(body: online.OnlineDetails) -> online.OnlineCalculatorResponse:
    """Calculate CO2 emissions for an online video call"""
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results


module_interface = ModuleInterface(
    name="online_calculator",
    entrypoint=online_calculator,
    request_type=online.OnlineDetails,
    response_type=online.OnlineCalculatorResponse,
    router=router,
)
