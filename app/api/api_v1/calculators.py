from app.api.api_v1.endpoints import online_calculator, train_calculator, \
    template_module, car_calculator, comparison_calculator, flight_calculator
from app.api.api_v1.calculator_interface import CalculatorInterfaces


calculators = CalculatorInterfaces(
    [
        car_calculator.module,
        comparison_calculator.module,
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
        train_calculator.module,
    ]
)
