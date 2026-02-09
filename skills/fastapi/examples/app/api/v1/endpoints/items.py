from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import Item, ItemCreate

router = APIRouter()

# In-memory storage for demo
items_db = []

@router.get("/", response_model=List[Item])
async def read_items():
    return items_db

@router.post("/", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    new_item = Item(id=len(items_db) + 1, **item.dict())
    items_db.append(new_item)
    return new_item

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
