from typing import Optional
from fastapi import FastAPI
from vc_calculator.interface import make_device, OnlineDetails, compute
import vc_calculator.interface as online

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.post("/online")
def calculate(body: online.OnlineDetails):
    devices = body.device_list
    devices = [online.make_device(d) for d in devices]
    results = online.compute(devices, body.bandwidth)
    return results
