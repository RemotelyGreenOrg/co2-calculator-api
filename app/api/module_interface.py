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
