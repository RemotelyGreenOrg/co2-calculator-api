import itertools
from typing import Any

from fastapi import FastAPI

from app.api import another_module, flight_calculator, template_module, vc_calculator
from app.api.module_interface import ModuleInterface


class Modules:
    def __init__(self: "Modules", module_interfaces: list[ModuleInterface]) -> None:
        self._modules = module_interfaces

    @property
    def modules(self: "Modules") -> list[ModuleInterface]:
        return self._modules

    @property
    def interfaces(self: "Modules") -> list[dict[str, Any]]:
        interfaces = [module.interface for module in self.modules]
        interfaces = list(itertools.chain.from_iterable(interfaces))
        return interfaces

    @property
    def request_schemas(self: "Modules") -> list[dict[str, Any]]:
        return [module.request_schema for module in self.modules]

    @property
    def response_schemas(self: "Modules") -> list[dict[str, Any]]:
        return [module.response_schema for module in self.modules]

    def include_routers(self: "Modules", app: FastAPI) -> None:
        for module in self.modules:
            app.include_router(module.router)


modules = Modules(
    [
        another_module.module,
        flight_calculator.module,
        template_module.module,
        vc_calculator.module,
    ]
)
