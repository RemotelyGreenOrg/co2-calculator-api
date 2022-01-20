from app.api import (
    flight_calculator,
    online_calculator,
    template_module, car_calculator,
)
from app.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        car_calculator.module,
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
    ]
)
