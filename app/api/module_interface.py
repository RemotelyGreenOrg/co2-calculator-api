import itertools
from typing import Any, Type, Generic, TypeVar, Callable

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class ModuleInterface(Generic[RequestT, ResponseT]):
    def __init__(
        self: "ModuleInterface",
        name: str,
        entrypoint: Callable[[RequestT], ResponseT],
        request_type: Type[RequestT],
        response_type: Type[ResponseT],
        router: APIRouter,
    ) -> None:
        self.router = router
        self.name = name
        self.entrypoint = entrypoint
        self._request_type = request_type
        self._response_type = response_type

    @property
    def request_type(self: "ModuleInterface") -> RequestT:
        return self._request_type

    @property
    def response_type(self: "ModuleInterface") -> ResponseT:
        return self._response_type

    @property
    def request_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.request_type.schema()

    @property
    def response_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.response_type.schema()

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
