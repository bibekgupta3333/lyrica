"""
Base CRUD operations.
Generic CRUD operations for all models.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with default methods for Create, Read, Update, Delete operations.
    
    Example:
        user_crud = CRUDBase(User)
        user = await user_crud.get(db, id=user_id)
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
        
        Returns:
            Model instance or None
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of model instances
        """
        result = await db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
        
        Returns:
            Created model instance
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Model instance to update
            obj_in: Pydantic schema or dict with update data
        
        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[ModelType]:
        """
        Delete a record.
        
        Args:
            db: Database session
            id: Record ID
        
        Returns:
            Deleted model instance or None
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
    
    async def count(self, db: AsyncSession) -> int:
        """
        Count total records.
        
        Args:
            db: Database session
        
        Returns:
            Total number of records
        """
        result = await db.execute(
            select(self.model).with_only_columns(self.model.id)
        )
        return len(result.all())

