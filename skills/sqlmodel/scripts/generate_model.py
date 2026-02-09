#!/usr/bin/env python3
"""Generate SQLModel model from specification."""

import argparse
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FieldSpec:
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    default: str | None = None
    foreign_key: str | None = None


def parse_field_spec(spec: str) -> FieldSpec:
    """Parse field specification string.

    Format: name:type[:options]
    Options: pk, null, unique, index, default=value, fk=table.column
    """
    parts = spec.split(":")
    name = parts[0]
    field_type = parts[1] if len(parts) > 1 else "str"

    field = FieldSpec(name=name, type=field_type)

    if len(parts) > 2:
        options = parts[2:]
        for opt in options:
            if opt == "pk":
                field.primary_key = True
            elif opt == "null":
                field.nullable = True
            elif opt == "unique":
                field.unique = True
            elif opt == "index":
                field.index = True
            elif opt.startswith("default="):
                field.default = opt.split("=", 1)[1]
            elif opt.startswith("fk="):
                field.foreign_key = opt.split("=", 1)[1]

    return field


def type_to_python(type_str: str) -> str:
    """Convert type string to Python type annotation."""
    type_map = {
        "int": "int",
        "str": "str",
        "string": "str",
        "text": "str",
        "bool": "bool",
        "boolean": "bool",
        "float": "float",
        "decimal": "float",
        "datetime": "datetime",
        "date": "date",
        "time": "time",
        "uuid": "UUID",
        "json": "dict",
        "list": "list",
    }
    return type_map.get(type_str.lower(), type_str)


def generate_field(field: FieldSpec) -> str:
    """Generate field definition string."""
    python_type = type_to_python(field.type)

    # Handle nullable
    if field.nullable or field.primary_key:
        python_type = f"{python_type} | None"

    # Build Field() arguments
    field_args = []

    if field.primary_key:
        field_args.append("primary_key=True")
        if field.default is None:
            field_args.insert(0, "default=None")

    if field.default is not None and not field.primary_key:
        if field.type in ("str", "string", "text"):
            field_args.append(f'default="{field.default}"')
        elif field.type in ("bool", "boolean"):
            field_args.append(f"default={field.default.capitalize()}")
        else:
            field_args.append(f"default={field.default}")
    elif field.nullable and not field.primary_key:
        field_args.append("default=None")

    if field.unique:
        field_args.append("unique=True")

    if field.index:
        field_args.append("index=True")

    if field.foreign_key:
        field_args.append(f'foreign_key="{field.foreign_key}"')

    # Generate line
    if field_args:
        return f"    {field.name}: {python_type} = Field({', '.join(field_args)})"
    else:
        return f"    {field.name}: {python_type}"


def generate_model(
    name: str,
    fields: list[FieldSpec],
    table: bool = True,
) -> str:
    """Generate complete model code."""
    # Imports
    imports = ["from sqlmodel import SQLModel, Field"]

    # Check for special types
    types_needed = set()
    for field in fields:
        if field.type in ("datetime", "date", "time"):
            types_needed.add(field.type)
        elif field.type == "uuid":
            types_needed.add("UUID")

    if "datetime" in types_needed or "date" in types_needed or "time" in types_needed:
        datetime_imports = [t for t in types_needed if t in ("datetime", "date", "time")]
        imports.append(f"from datetime import {', '.join(datetime_imports)}")

    if "UUID" in types_needed:
        imports.append("from uuid import UUID")

    # Build model
    table_arg = ", table=True" if table else ""
    lines = [
        "\n".join(imports),
        "",
        "",
        f"class {name}(SQLModel{table_arg}):",
        f'    """Database model for {name}."""',
        "",
    ]

    for field in fields:
        lines.append(generate_field(field))

    return "\n".join(lines)


def generate_schemas(name: str, fields: list[FieldSpec]) -> str:
    """Generate API schema models."""
    # Filter out internal fields for create schema
    create_fields = [f for f in fields if not f.primary_key and f.name not in ("created_at", "updated_at")]

    lines = [
        f"# API Schemas for {name}",
        "",
        f"class {name}Base(SQLModel):",
        f'    """{name} base schema with shared fields."""',
    ]

    for field in create_fields:
        if not field.foreign_key:
            lines.append(generate_field(field))

    lines.extend([
        "",
        "",
        f"class {name}Create({name}Base):",
        f'    """Schema for creating {name}."""',
        "    pass",
        "",
        "",
        f"class {name}Read({name}Base):",
        f'    """Schema for reading {name}."""',
    ])

    # Add id and other read-only fields
    for field in fields:
        if field.primary_key:
            lines.append(f"    {field.name}: {type_to_python(field.type)}")

    lines.extend([
        "",
        "",
        f"class {name}Update(SQLModel):",
        f'    """Schema for updating {name}. All fields optional."""',
    ])

    for field in create_fields:
        if not field.foreign_key:
            python_type = type_to_python(field.type)
            lines.append(f"    {field.name}: {python_type} | None = None")

    return "\n".join(lines)


def generate_crud(name: str) -> str:
    """Generate CRUD operations."""
    lower_name = name.lower()

    return f'''"""CRUD operations for {name}."""

from sqlmodel import Session, select
from .models import {name}, {name}Create, {name}Update


def create_{lower_name}(session: Session, {lower_name}: {name}Create) -> {name}:
    """Create a new {lower_name}."""
    db_{lower_name} = {name}.model_validate({lower_name})
    session.add(db_{lower_name})
    session.commit()
    session.refresh(db_{lower_name})
    return db_{lower_name}


def get_{lower_name}(session: Session, {lower_name}_id: int) -> {name} | None:
    """Get {lower_name} by ID."""
    return session.get({name}, {lower_name}_id)


def get_{lower_name}s(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[{name}]:
    """Get list of {lower_name}s."""
    statement = select({name}).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_{lower_name}(
    session: Session,
    {lower_name}_id: int,
    {lower_name}_data: {name}Update,
) -> {name} | None:
    """Update {lower_name}."""
    db_{lower_name} = session.get({name}, {lower_name}_id)
    if not db_{lower_name}:
        return None

    update_data = {lower_name}_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_{lower_name}, key, value)

    session.add(db_{lower_name})
    session.commit()
    session.refresh(db_{lower_name})
    return db_{lower_name}


def delete_{lower_name}(session: Session, {lower_name}_id: int) -> bool:
    """Delete {lower_name}."""
    db_{lower_name} = session.get({name}, {lower_name}_id)
    if not db_{lower_name}:
        return False

    session.delete(db_{lower_name})
    session.commit()
    return True
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate SQLModel model from specification"
    )
    parser.add_argument("name", help="Model name (e.g., User, Product)")
    parser.add_argument(
        "fields",
        nargs="+",
        help="Field specs: name:type[:options] (e.g., id:int:pk, email:str:unique)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path"
    )
    parser.add_argument(
        "--schemas",
        action="store_true",
        help="Generate API schemas"
    )
    parser.add_argument(
        "--crud",
        action="store_true",
        help="Generate CRUD operations"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate model, schemas, and CRUD"
    )

    args = parser.parse_args()

    # Parse fields
    fields = [parse_field_spec(f) for f in args.fields]

    # Generate model
    model_code = generate_model(args.name, fields)
    print("# Model")
    print("=" * 50)
    print(model_code)

    if args.schemas or args.all:
        print("\n\n# Schemas")
        print("=" * 50)
        print(generate_schemas(args.name, fields))

    if args.crud or args.all:
        print("\n\n# CRUD Operations")
        print("=" * 50)
        print(generate_crud(args.name))

    # Write to file if specified
    if args.output:
        output_content = model_code
        if args.schemas or args.all:
            output_content += "\n\n" + generate_schemas(args.name, fields)

        args.output.write_text(output_content, encoding="utf-8")
        print(f"\nWritten to: {args.output}")


if __name__ == "__main__":
    main()
