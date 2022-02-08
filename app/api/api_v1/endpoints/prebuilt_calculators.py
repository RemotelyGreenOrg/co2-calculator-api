from . import flight_calculator as inperson
from . import online_calculator as online


def build_inperson_request(event):
    stages = []

    end = inperson.GeoCoordinates(
                lat=event.location["latitude"],
                lon=event.location["longitude"])
    for participant in event.participants:
        start = inperson.GeoCoordinates(
                    lat=participant.location["latitude"],
                    lon=participant.location["longitude"])
        single_stage = dict(start=start, end=end, one_way=False)
        stages.append(single_stage)
    request = dict(stages=stages)
    return inperson.FlightCalculatorRequest(**request)


def build_online_request(event):
    pass


class BasicCalculator():
    def __init__(self):
        self.basic_device_list = []

    async def __call__(self, event):
        results_inperson = await inperson.flight_calculator(build_inperson_request(event))
        #results_online = await online.online_calculator(build_online_request(event))

        return results_inperson.dict()
