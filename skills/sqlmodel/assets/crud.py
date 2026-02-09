"""Generic CRUD operations template for SQLModel (async)."""

from typing import TypeVar, Generic, Type, Any
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

# Type variables for generic CRUD
ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.

    Usage:
        class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
            pass

        user_crud = UserCRUD(User)
        user = await user_crud.get(session, user_id)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        id: int,
    ) -> ModelType | None:
        """Get a single record by ID."""
        return await session.get(self.model, id)

    async def get_with_relations(
        self,
        session: AsyncSession,
        id: int,
        *relations: Any,
    ) -> ModelType | None:
        """Get a single record by ID with eager-loaded relations."""
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(*[selectinload(r) for r in relations])
        )
        result = await session.exec(statement)
        return result.first()

    async def get_by_field(
        self,
        session: AsyncSession,
        field: str,
        value: Any,
    ) -> ModelType | None:
        """Get a single record by field value."""
        statement = select(self.model).where(
            getattr(self.model, field) == value
        )
        result = await session.exec(statement)
        return result.first()

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.all()

    async def get_multi_by_field(
        self,
        session: AsyncSession,
        field: str,
        value: Any,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get multiple records filtered by field value."""
        statement = (
            select(self.model)
            .where(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
        )
        result = await session.exec(statement)
        return result.all()

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """Create a new record."""
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def create_with_data(
        self,
        session: AsyncSession,
        **data: Any,
    ) -> ModelType:
        """Create a new record from keyword arguments."""
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        id: int,
        obj_in: UpdateSchemaType,
    ) -> ModelType | None:
        """Update an existing record."""
        db_obj = await session.get(self.model, id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_with_data(
        self,
        session: AsyncSession,
        *,
        id: int,
        **data: Any,
    ) -> ModelType | None:
        """Update an existing record from keyword arguments."""
        db_obj = await session.get(self.model, id)
        if not db_obj:
            return None

        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        session: AsyncSession,
        *,
        id: int,
    ) -> bool:
        """Delete a record by ID."""
        db_obj = await session.get(self.model, id)
        if not db_obj:
            return False

        await session.delete(db_obj)
        await session.commit()
        return True

    async def count(self, session: AsyncSession) -> int:
        """Count total records."""
        from sqlmodel import func
        statement = select(func.count(self.model.id))
        result = await session.exec(statement)
        return result.one()

    async def exists(
        self,
        session: AsyncSession,
        id: int,
    ) -> bool:
        """Check if a record exists."""
        db_obj = await session.get(self.model, id)
        return db_obj is not None

    async def exists_by_field(
        self,
        session: AsyncSession,
        field: str,
        value: Any,
    ) -> bool:
        """Check if a record exists by field value."""
        statement = select(self.model.id).where(
            getattr(self.model, field) == value
        )
        result = await session.exec(statement)
        return result.first() is not None


# =============================================================================
# Example Usage
# =============================================================================

# from .models import User, UserCreate, UserUpdate
#
# class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
#     """User-specific CRUD with additional methods."""
#
#     async def get_by_email(
#         self,
#         session: AsyncSession,
#         email: str,
#     ) -> User | None:
#         return await self.get_by_field(session, "email", email)
#
#     async def get_active_users(
#         self,
#         session: AsyncSession,
#         skip: int = 0,
#         limit: int = 100,
#     ) -> list[User]:
#         return await self.get_multi_by_field(
#             session, "is_active", True, skip=skip, limit=limit
#         )
#
# user_crud = UserCRUD(User)
