from typing import Any

import vc_calculator.interface as online
from fastapi import APIRouter

router = APIRouter()


@router.post("/online")
def online_calculator(body: online.OnlineDetails) -> online.OnlineCalculatorResponse:
    """Calculate CO2 emissions for an online video call"""
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results


def interface() -> list[dict[str, Any]]:
    return [online.OnlineDetails.schema(), online.OnlineCalculatorResponse.schema()]


def request() -> dict[str, Any]:
    return online.OnlineDetails.schema()


def response() -> dict[str, Any]:
    return online.OnlineCalculatorResponse.schema()
