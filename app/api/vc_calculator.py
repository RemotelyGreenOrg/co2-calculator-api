import vc_calculator.interface as online
from vc_calculator.interface import OnlineDetails, OnlineCalculatorResponse
from fastapi import APIRouter

from app.api.module_interface import ModuleInterface

router = APIRouter()


@router.post("/online", response_model=OnlineCalculatorResponse)
async def online_calculator(body: OnlineDetails) -> OnlineCalculatorResponse:
    """Calculate CO2 emissions for an online video call"""
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results


module = ModuleInterface(
    name="online_calculator",
    entrypoint=online_calculator,
    request_type=OnlineDetails,
    response_type=OnlineCalculatorResponse,
    router=router,
)
