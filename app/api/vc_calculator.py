import vc_calculator.interface as online
from fastapi import APIRouter


router = APIRouter()


@router.post("/online")
def calculate(body: online.OnlineDetails):
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results
