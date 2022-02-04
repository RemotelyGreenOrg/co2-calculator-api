from .api import flight_calculator as inperson
from .api import online_calculator as online


def build_inperson_request(event):
    stages = []
    for participant in event.participants:
        print("BEK", participant)
        single_stage = dict(start=participant.location, end=event.location, one_way=False)
        stages.append(single_stage)
    request = dict(stages=stages)
    return inperson.FlightCalculatorRequest(**request)


class BasicCalculator():
    def __init__(self):
        self.basic_device_list = []


    def __call__(self, event):
        results_inperson = inperson.flight_calculator(build_inperson_request(event))

        return 42 * event.num_participants
