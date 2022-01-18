from app.api import (
    another_module,
    flight_calculator,
    online_calculator,
    template_module,
)
from app.api.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        another_module.module,
        flight_calculator.module,
        online_calculator.module,
        template_module.module,
    ]
)
