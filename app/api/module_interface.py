import itertools
from typing import Any, Type, Generic, TypeVar, Callable

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class Module(Generic[RequestT, ResponseT]):
    def __init__(
        self: "Module",
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
    def request_type(self: "Module") -> RequestT:
        return self._request_type

    @property
    def response_type(self: "Module") -> ResponseT:
        return self._response_type

    @property
    def request_schema(self: "Module") -> dict[str, Any]:
        return self.request_type.schema()

    @property
    def response_schema(self: "Module") -> dict[str, Any]:
        return self.response_type.schema()

    @property
    def interface(self: "Module") -> tuple[dict[str, Any], dict[str, Any]]:
        return self.request_schema, self.response_schema


class Modules:
    def __init__(self: "Modules", modules: list[Module]) -> None:
        self._modules = modules

    @property
    def modules(self: "Modules") -> list[Module]:
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
