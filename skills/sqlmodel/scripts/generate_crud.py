#!/usr/bin/env python3
"""Generate CRUD operations and FastAPI endpoints for SQLModel."""

import argparse
from pathlib import Path


def generate_sync_crud(model_name: str) -> str:
    """Generate synchronous CRUD operations."""
    lower = model_name.lower()

    return f'''"""Synchronous CRUD operations for {model_name}."""

from sqlmodel import Session, select
from .models import {model_name}, {model_name}Create, {model_name}Update


def create_{lower}(session: Session, data: {model_name}Create) -> {model_name}:
    """Create a new {lower}."""
    db_obj = {model_name}.model_validate(data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_{lower}(session: Session, {lower}_id: int) -> {model_name} | None:
    """Get {lower} by ID."""
    return session.get({model_name}, {lower}_id)


def get_{lower}s(
    session: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[{model_name}]:
    """Get list of {lower}s with pagination."""
    statement = select({model_name}).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_{lower}_by_field(
    session: Session,
    field_name: str,
    value: any,
) -> {model_name} | None:
    """Get {lower} by a specific field value."""
    statement = select({model_name}).where(
        getattr({model_name}, field_name) == value
    )
    return session.exec(statement).first()


def update_{lower}(
    session: Session,
    {lower}_id: int,
    data: {model_name}Update,
) -> {model_name} | None:
    """Update {lower} by ID."""
    db_obj = session.get({model_name}, {lower}_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_{lower}(session: Session, {lower}_id: int) -> bool:
    """Delete {lower} by ID."""
    db_obj = session.get({model_name}, {lower}_id)
    if not db_obj:
        return False

    session.delete(db_obj)
    session.commit()
    return True


def count_{lower}s(session: Session) -> int:
    """Count total {lower}s."""
    from sqlmodel import func
    statement = select(func.count({model_name}.id))
    return session.exec(statement).one()
'''


def generate_async_crud(model_name: str) -> str:
    """Generate asynchronous CRUD operations."""
    lower = model_name.lower()

    return f'''"""Asynchronous CRUD operations for {model_name}."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import {model_name}, {model_name}Create, {model_name}Update


async def create_{lower}(session: AsyncSession, data: {model_name}Create) -> {model_name}:
    """Create a new {lower}."""
    db_obj = {model_name}.model_validate(data)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def get_{lower}(session: AsyncSession, {lower}_id: int) -> {model_name} | None:
    """Get {lower} by ID."""
    return await session.get({model_name}, {lower}_id)


async def get_{lower}s(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[{model_name}]:
    """Get list of {lower}s with pagination."""
    statement = select({model_name}).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def get_{lower}_by_field(
    session: AsyncSession,
    field_name: str,
    value: any,
) -> {model_name} | None:
    """Get {lower} by a specific field value."""
    statement = select({model_name}).where(
        getattr({model_name}, field_name) == value
    )
    result = await session.exec(statement)
    return result.first()


async def update_{lower}(
    session: AsyncSession,
    {lower}_id: int,
    data: {model_name}Update,
) -> {model_name} | None:
    """Update {lower} by ID."""
    db_obj = await session.get({model_name}, {lower}_id)
    if not db_obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def delete_{lower}(session: AsyncSession, {lower}_id: int) -> bool:
    """Delete {lower} by ID."""
    db_obj = await session.get({model_name}, {lower}_id)
    if not db_obj:
        return False

    await session.delete(db_obj)
    await session.commit()
    return True


async def count_{lower}s(session: AsyncSession) -> int:
    """Count total {lower}s."""
    from sqlmodel import func
    statement = select(func.count({model_name}.id))
    result = await session.exec(statement)
    return result.one()
'''


def generate_fastapi_router(model_name: str, async_mode: bool = True) -> str:
    """Generate FastAPI router with endpoints."""
    lower = model_name.lower()
    plural = f"{lower}s"

    if async_mode:
        return f'''"""FastAPI router for {model_name} (async)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import get_session
from .models import {model_name}, {model_name}Create, {model_name}Read, {model_name}Update
from . import crud

router = APIRouter(prefix="/{plural}", tags=["{plural}"])


@router.post("/", response_model={model_name}Read, status_code=201)
async def create_{lower}(
    data: {model_name}Create,
    session: AsyncSession = Depends(get_session),
):
    """Create a new {lower}."""
    return await crud.create_{lower}(session, data)


@router.get("/{{id}}", response_model={model_name}Read)
async def get_{lower}(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get {lower} by ID."""
    {lower} = await crud.get_{lower}(session, id)
    if not {lower}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {lower}


@router.get("/", response_model=list[{model_name}Read])
async def get_{plural}(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    """Get list of {plural}."""
    return await crud.get_{lower}s(session, skip=skip, limit=limit)


@router.patch("/{{id}}", response_model={model_name}Read)
async def update_{lower}(
    id: int,
    data: {model_name}Update,
    session: AsyncSession = Depends(get_session),
):
    """Update {lower} by ID."""
    {lower} = await crud.update_{lower}(session, id, data)
    if not {lower}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {lower}


@router.delete("/{{id}}", status_code=204)
async def delete_{lower}(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete {lower} by ID."""
    if not await crud.delete_{lower}(session, id):
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return None
'''
    else:
        return f'''"""FastAPI router for {model_name} (sync)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from .database import get_session
from .models import {model_name}, {model_name}Create, {model_name}Read, {model_name}Update
from . import crud

router = APIRouter(prefix="/{plural}", tags=["{plural}"])


@router.post("/", response_model={model_name}Read, status_code=201)
def create_{lower}(
    data: {model_name}Create,
    session: Session = Depends(get_session),
):
    """Create a new {lower}."""
    return crud.create_{lower}(session, data)


@router.get("/{{id}}", response_model={model_name}Read)
def get_{lower}(
    id: int,
    session: Session = Depends(get_session),
):
    """Get {lower} by ID."""
    {lower} = crud.get_{lower}(session, id)
    if not {lower}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {lower}


@router.get("/", response_model=list[{model_name}Read])
def get_{plural}(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get list of {plural}."""
    return crud.get_{lower}s(session, skip=skip, limit=limit)


@router.patch("/{{id}}", response_model={model_name}Read)
def update_{lower}(
    id: int,
    data: {model_name}Update,
    session: Session = Depends(get_session),
):
    """Update {lower} by ID."""
    {lower} = crud.update_{lower}(session, id, data)
    if not {lower}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {lower}


@router.delete("/{{id}}", status_code=204)
def delete_{lower}(
    id: int,
    session: Session = Depends(get_session),
):
    """Delete {lower} by ID."""
    if not crud.delete_{lower}(session, id):
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return None
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate CRUD operations and FastAPI endpoints"
    )
    parser.add_argument("model", help="Model name (e.g., User, Product)")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Generate synchronous code (default: async)"
    )
    parser.add_argument(
        "--crud-only",
        action="store_true",
        help="Generate only CRUD, no router"
    )
    parser.add_argument(
        "--router-only",
        action="store_true",
        help="Generate only router, no CRUD"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output directory"
    )

    args = parser.parse_args()
    async_mode = not args.sync

    # Generate CRUD
    if not args.router_only:
        print("# CRUD Operations")
        print("=" * 60)
        if async_mode:
            print(generate_async_crud(args.model))
        else:
            print(generate_sync_crud(args.model))

    # Generate Router
    if not args.crud_only:
        print("\n\n# FastAPI Router")
        print("=" * 60)
        print(generate_fastapi_router(args.model, async_mode))

    # Write to files if output specified
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

        if not args.router_only:
            crud_file = args.output / "crud.py"
            crud_content = generate_async_crud(args.model) if async_mode else generate_sync_crud(args.model)
            crud_file.write_text(crud_content, encoding="utf-8")
            print(f"\nWritten: {crud_file}")

        if not args.crud_only:
            router_file = args.output / "router.py"
            router_content = generate_fastapi_router(args.model, async_mode)
            router_file.write_text(router_content, encoding="utf-8")
            print(f"Written: {router_file}")


if __name__ == "__main__":
    main()
