from enum import Enum
from pydantic import BaseModel, confloat


class GeoCoordinates(BaseModel):
    lon: confloat(ge=-180.0, lt=180.0)
    lat: confloat(ge=-90.0, lt=90.0)


class Country(BaseModel):
    iso_code: str
    name: str
    coordinates: GeoCoordinates


JoinMode = Enum('JoinMode', 'online in_person')
