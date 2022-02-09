from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base


if TYPE_CHECKING:
    from .participant import Participant  # noqa


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lon = Column(Float)
    lat = Column(Float)
    participants = relationship("Participant")
