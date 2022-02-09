from app.api.api_v1.endpoints import (
    car_calculator,
    comparison_calculator,
    flight_calculator,
    online_calculator,
    template_calculator,
    train_calculator,
)
from app.api.api_v1.calculator_interface import CalculatorInterfaces


calculators = CalculatorInterfaces(
    [
        car_calculator.calculator_interface,
        comparison_calculator.calculator_interface,
        flight_calculator.calculator_interface,
        online_calculator.calculator_interface,
        template_calculator.calculator_interface,
        train_calculator.calculator_interface,
    ]
)
