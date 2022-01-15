from typing import Any, Type, Generic, TypeVar, Callable

from fastapi import APIRouter
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
        self.request_type = request_type
        self.response_type = response_type

    def interface(self: "ModuleInterface") -> list[dict[str, Any]]:
        return [self.request_schema(), self.response_schema()]

    def request_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.request_type.schema()

    def response_schema(self: "ModuleInterface") -> dict[str, Any]:
        return self.response_type.schema()
