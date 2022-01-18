import itertools
from typing import Any, Type, Generic, TypeVar, Callable, Awaitable, Optional

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from pydantic.generics import GenericModel

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class ModuleInterface(GenericModel, Generic[RequestT, ResponseT]):
    name: str
    path: str
    entrypoint: Callable[[RequestT], Awaitable[ResponseT]]
    request_model: Type[RequestT]
    response_model: Type[ResponseT]
    method: str = "post"
    router_args: Optional[dict[str, Any]] = None

    @property
    def request_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.request_model.schema()

    @property
    def response_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.response_model.schema()

    @property
    def interface(self: "ModuleInterface") -> tuple[dict[str, Any], dict[str, Any]]:
        return self.request_schema, self.response_schema


class ModuleInterfaces:
    def __init__(
        self: "ModuleInterfaces", module_interfaces: list[ModuleInterface]
    ) -> None:
        self._modules = module_interfaces
        self._modules_by_name = {m.name: m for m in module_interfaces}

    @property
    def modules(self: "ModuleInterfaces") -> list[ModuleInterface]:
        return self._modules

    @property
    def modules_by_name(self: "ModuleInterfaces") -> dict[str, ModuleInterface]:
        return self._modules_by_name

    @property
    def interfaces(self: "ModuleInterfaces") -> list[dict[str, Any]]:
        interfaces = [module.interface for module in self.modules]
        interfaces = list(itertools.chain.from_iterable(interfaces))
        return interfaces

    @property
    def request_schemas(self: "ModuleInterfaces") -> list[dict[str, Any]]:
        return [module.request_schema for module in self.modules]

    @property
    def response_schemas(self: "ModuleInterfaces") -> list[dict[str, Any]]:
        return [module.response_schema for module in self.modules]

    def include_routers(self: "ModuleInterfaces", app: FastAPI) -> None:
        for module in self.modules:
            app.include_router(module.router)
