from app.api import (
    flight_calculator,
    online_calculator,
    template_module,
)
from app.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
    ]
)
