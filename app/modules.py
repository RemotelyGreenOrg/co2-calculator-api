from app.api import (
    comparison_calculator,
    flight_calculator,
    online_calculator,
    template_module,
)
from app.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        comparison_calculator.module,
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
    ]
)
