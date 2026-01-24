"""Items API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.database import db_service

router = APIRouter()


class PurchaseRequest(BaseModel):
    player_uuid: str
    item_id: str


@router.get("/")
async def get_all_items():
    """Get all available items."""
    items = await db_service.get_all_items()
    return {"items": items}


@router.get("/{item_id}")
async def get_item(item_id: str):
    """Get item by ID."""
    item = await db_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/purchase")
async def purchase_item(request: PurchaseRequest):
    """Purchase an item (deduct balance, credit trader)."""
    user = await db_service.get_user_by_uuid(request.player_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    item = await db_service.get_item_by_id(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    price = int(item.get("price", 0))
    if user["balance"] < price:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # deduct from player
    new_balance = user["balance"] - price
    await db_service.update_balance(request.player_uuid, new_balance)

    # credit trader if exists
    trader_id = item.get("trader_id")
    if trader_id:
        trader = await db_service.get_trader_by_id(trader_id)
        if trader:
            new_trader_balance = int(trader.get("balance", 0)) + price
            await db_service.update_trader_balance(trader_id, new_trader_balance)

    # log transaction
    await db_service.log_transaction(
        from_type="player",
        from_id=request.player_uuid,
        to_type="trader" if trader_id else "system",
        to_id=trader_id or "SYSTEM",
        amount=price,
        tx_type="purchase",
        description=f"Покупка: {item.get('name', request.item_id)}"
    )

    return {
        "success": True,
        "item": item,
        "paid": price,
        "new_balance": new_balance
    }
