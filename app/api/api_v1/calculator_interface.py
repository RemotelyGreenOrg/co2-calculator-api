import itertools
from typing import Any, Type, Generic, TypeVar, Callable, Awaitable, Optional

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from pydantic.generics import GenericModel

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class CalculatorInterface(GenericModel, Generic[RequestT, ResponseT]):
    name: str
    path: str
    entrypoint: Callable[[RequestT], Awaitable[ResponseT]]
    request_model: Type[RequestT]
    response_model: Type[ResponseT]
    method: str = "post"
    router_args: Optional[dict[str, Any]] = None
    get_total_carbon_kg: Callable[[ResponseT], float]

    @property
    def request_schema(self: "CalculatorInterface") -> dict[str, Any]:
        return self.request_model.schema()

    @property
    def response_schema(self: "CalculatorInterface") -> dict[str, Any]:
        return self.response_model.schema()

    @property
    def interface(self: "CalculatorInterface") -> tuple[dict[str, Any], dict[str, Any]]:
        return self.request_schema, self.response_schema


class CalculatorInterfaces:
    def __init__(
        self: "CalculatorInterfaces", calculator_interfaces: list[CalculatorInterface]
    ) -> None:
        self._calculators = calculator_interfaces
        self._calculators_by_name = {m.name: m for m in calculator_interfaces}

    @property
    def calculators(self: "CalculatorInterfaces") -> list[CalculatorInterface]:
        return self._calculators

    @property
    def calculators_by_name(
        self: "CalculatorInterfaces",
    ) -> dict[str, CalculatorInterface]:
        return self._calculators_by_name

    @property
    def interfaces(self: "CalculatorInterfaces") -> list[dict[str, Any]]:
        interfaces = [calculator.interface for calculator in self.calculators]
        interfaces = list(itertools.chain.from_iterable(interfaces))
        return interfaces

    @property
    def request_schemas(self: "CalculatorInterfaces") -> list[dict[str, Any]]:
        return [calculator.request_schema for calculator in self.calculators]

    @property
    def response_schemas(self: "CalculatorInterfaces") -> list[dict[str, Any]]:
        return [calculator.response_schema for calculator in self.calculators]

    async def get_calculators(
        self: "CalculatorInterfaces",
    ) -> dict[str, list[dict[str, Any]]]:
        return {"calculators": self.interfaces}

    async def get_requests(
        self: "CalculatorInterfaces",
    ) -> dict[str, list[dict[str, Any]]]:
        return {"requests": self.request_schemas}

    async def get_responses(
        self: "CalculatorInterfaces",
    ) -> dict[str, list[dict[str, Any]]]:
        return {"responses": self.response_schemas}

    def register(self: "CalculatorInterfaces", app: FastAPI) -> None:
        router = APIRouter()

        for calculator in self.calculators:
            router.add_api_route(
                path=calculator.path,
                endpoint=calculator.entrypoint,
                name=calculator.name,
                methods=[calculator.method],
                response_model=calculator.response_model,
                **(calculator.router_args or {}),
            )

        app.add_route("/calculators", self.get_calculators)
        app.add_route("/calculator-requests", self.get_requests)
        app.add_route("/calculator-responses", self.get_responses)
        app.include_router(router)
