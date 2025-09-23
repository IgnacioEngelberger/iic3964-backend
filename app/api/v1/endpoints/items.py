from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


# Mock data for demonstration
items_db = [
    Item(id=1, name="Item 1", description="Description 1", price=10.99),
    Item(id=2, name="Item 2", description="Description 2", price=20.99),
]


@router.get("/", response_model=List[Item])
async def get_items() -> List[Item]:
    return items_db


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    item = next((item for item in items_db if item.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=Item)
async def create_item(item: ItemCreate) -> Item:
    new_id = max([item.id for item in items_db], default=0) + 1
    new_item = Item(id=new_id, **item.dict())
    items_db.append(new_item)
    return new_item
