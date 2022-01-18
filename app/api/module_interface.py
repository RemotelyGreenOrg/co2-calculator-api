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
    get_total_carbon_kg: Callable[[ResponseT], float]

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

    async def get_modules(self: "ModuleInterfaces") -> dict[str, list[dict[str, Any]]]:
        return {"modules": self.interfaces}

    async def get_requests(self: "ModuleInterfaces") -> dict[str, list[dict[str, Any]]]:
        return {"requests": self.request_schemas}

    async def get_responses(self: "ModuleInterfaces") -> dict[str, list[dict[str, Any]]]:
        return {"responses": self.response_schemas}

    def register(self: "ModuleInterfaces", app: FastAPI) -> None:
        router = APIRouter()

        for module in self.modules:
            router.add_api_route(
                path=module.path,
                endpoint=module.entrypoint,
                name=module.name,
                methods=[module.method],
                response_model=module.response_model,
                **(module.router_args or {}),
            )

        app.add_route("/modules", self.get_modules)
        app.add_route("/requests", self.get_requests)
        app.add_route("/responses", self.get_responses)
        app.include_router(router)
