from app.api import another_module, flight_calculator, template_module, vc_calculator
from app.api.module_interface import ModuleInterfaces


modules = ModuleInterfaces(
    [
        another_module.module,
        flight_calculator.module,
        template_module.module,
        vc_calculator.module,
    ]
)
