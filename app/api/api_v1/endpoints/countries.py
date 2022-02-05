from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/{id}", response_model=schemas.Country)
def read_country(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Get country by ID"""
    result = crud.country.get(db=db, id=id, raise_unfound=True)
    return result


@router.get("/", response_model=list[schemas.Country])
def read_countries(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve countries"""
    result = crud.country.get_multi(db=db, skip=skip, limit=limit)
    return result


@router.post("/", response_model=schemas.Country)
def create_country(
    *,
    db: Session = Depends(deps.get_db),
    country_in: schemas.CountryCreate,
) -> Any:
    """Create new country"""
    result = crud.country.create(db=db, obj_in=country_in)
    return result


@router.put("/{id}", response_model=schemas.Country)
def update_country(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    country_in: schemas.CountryUpdate,
) -> Any:
    """Update a country"""
    result = crud.country.find_and_update(db=db, id=id, obj_in=country_in)
    return result


@router.delete("/{id}", response_model=schemas.Country)
def delete_country(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Delete a country"""
    result = crud.country.find_and_remove(db=db, id=id)
    return result
