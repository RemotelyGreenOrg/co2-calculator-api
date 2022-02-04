from typing import Optional

from pydantic import BaseModel


# Shared properties
class CountryBase(BaseModel):
    iso_code: Optional[str] = None
    name: Optional[str] = None


# Properties to receive on country creation
class CountryCreate(CountryBase):
    iso_code: str
    name: str


# Properties to receive on country update
class CountryUpdate(CountryBase):
    pass


# Properties shared by models stored in DB
class CountryInDBBase(CountryBase):
    id: int
    iso_code: str
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class Country(CountryInDBBase):
    pass


# Properties properties stored in DB
class CountryInDB(CountryInDBBase):
    pass
