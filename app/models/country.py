from sqlalchemy import Column, Integer, String

from app.db.base_class import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    iso_code = Column(String, index=True)
    name = Column(String)
