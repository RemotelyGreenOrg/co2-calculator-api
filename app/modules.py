from app.api import (
    car_calculator,
    comparison_calculator,
    flight_calculator,
    online_calculator,
    template_module,
    train_calculator,
)
from app.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        car_calculator.module,
        comparison_calculator.module,
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
        train_calculator.module,
    ]
)
