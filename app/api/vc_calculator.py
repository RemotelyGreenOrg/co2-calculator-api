import vc_calculator.interface as online
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter()

class vc_calculatorRequest(BaseModel):
    """
    This is the Virtual conference calculator Request
    """

    snap: int = Field(
        42,
        title='The Snap',
        description='this is the value of snap',
        ge=0,
        lt=100,
    )

    class Config:
        title = 'Virtual Conference Calculator Request'

class vc_calculatorResponse(BaseModel):
    """
    This is the Virtual conference calculator Response
    """
    class Config:
        title = 'Virtual Conference Calculator Response'

@router.post("/online")
def online_calculator(body: online.OnlineDetails) -> online.OnlineCalculatorResponse:
    """Calculate CO2 emissions for an online video call"""
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results

def interface():
    return [vc_calculatorRequest.schema(),vc_calculatorResponse.schema()]

def request():
    return vc_calculatorRequest.schema()

def response():
    return vc_calculatorResponse.schema()