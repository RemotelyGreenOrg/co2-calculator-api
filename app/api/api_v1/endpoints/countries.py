from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
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
    """
    Get country by ID.
    """
    country = crud.country.get(db=db, id=id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return country


@router.get("/", response_model=List[schemas.Country])
def read_countries(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve countries.
    """
    countries = crud.country.get_multi(db=db, skip=skip, limit=limit)
    return countries


@router.post("/", response_model=schemas.Country)
def create_country(
    *,
    db: Session = Depends(deps.get_db),
    country_in: schemas.CountryCreate,
) -> Any:
    """
    Create new country.
    """
    country = crud.country.create(db=db, obj_in=country_in)
    return country


@router.put("/{id}", response_model=schemas.Country)
def update_country(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    country_in: schemas.CountryUpdate,
) -> Any:
    """
    Update a country.
    """
    country = crud.country.get(db=db, id=id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    country = crud.country.update(db=db, db_obj=country, obj_in=country_in)
    return country


@router.delete("/{id}", response_model=schemas.Country)
def delete_country(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete a country.
    """
    country = crud.country.get(db=db, id=id)

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    country = crud.country.remove(db=db, id=id)
    return country
