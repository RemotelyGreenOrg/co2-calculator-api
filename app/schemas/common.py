from enum import Enum

from pydantic import BaseModel, confloat


class JoinMode(str, Enum):
    """Ways in which event participants can join"""

    online = "online"
    in_person = "in_person"


class GeoCoordinates(BaseModel):
    """Schema for a lon-lat geo-location"""

    lon: confloat(ge=-180.0, lt=180.0)
    lat: confloat(ge=-90.0, lt=90.0)
