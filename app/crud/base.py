from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD)

        Args:
            model: A SQLAlchemy model class
        """
        self.classname = model.__class__.__name__
        self.tablename = model.__tablename__
        self.model = model

    def get(
        self,
        db: Session,
        id: Any,
        raise_unfound: bool = False,
    ) -> Optional[ModelType]:
        result = db.query(self.model).filter(self.model.id == id).first()

        if raise_unfound:
            self._raise_if_unfound(result)

        return result

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def find_and_update(
        self,
        db: Session,
        *,
        id: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        db_obj = self.get(db=db, id=id, raise_unfound=True)
        db_obj = self.update(db=db, db_obj=db_obj, obj_in=obj_in)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def find_and_remove(
        self,
        *,
        db: Session,
        id: int
    ) -> ModelType:
        self.get(db=db, id=id, raise_unfound=True)
        db_obj = self.remove(db=db, id=id)
        return db_obj

    def _raise_if_unfound(self, obj: ModelType) -> None:
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.classname} not found")
