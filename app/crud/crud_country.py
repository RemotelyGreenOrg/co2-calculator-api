from app.crud.base import CRUDBase
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    pass


country = CRUDCountry(Country)
