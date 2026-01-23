"""Items API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.sheets import sheets_service

router = APIRouter()


class PurchaseRequest(BaseModel):
    player_uuid: str
    item_id: str


@router.get("/")
async def get_all_items():
    """Get all available items."""
    items = sheets_service.get_all_items()
    return {"items": items}


@router.get("/{item_id}")
async def get_item(item_id: str):
    """Get item by ID."""
    item = sheets_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/purchase")
async def purchase_item(request: PurchaseRequest):
    """Purchase an item (deduct balance)."""
    user = sheets_service.get_user_by_uuid(request.player_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    item = sheets_service.get_item_by_id(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    price = int(item.get("price", 0))
    if user["balance"] < price:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    new_balance = user["balance"] - price
    sheets_service.update_balance(request.player_uuid, new_balance)

    return {
        "success": True,
        "item": item,
        "paid": price,
        "new_balance": new_balance
    }
