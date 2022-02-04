from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, Float, Boolean, Enum, ForeignKey

from app.db.base_class import Base
from app.schemas.common import JoinMode

if TYPE_CHECKING:
    from .event import Event  # noqa


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    join_mode = Column(Enum(JoinMode))
    lon = Column(Float)
    lat = Column(Float)
    active = Column(Boolean)
    event_id = Column(Integer, ForeignKey('events.id'))
