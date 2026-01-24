"""QR code parsing API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.database import db_service

router = APIRouter()


class QRParseRequest(BaseModel):
    data: str


@router.post("/parse")
async def parse_qr(request: QRParseRequest):
    """
    Parse QR code data and return type and related info.

    QR formats:
    - LOGIN:UUID - login as user
    - PAY:ITEM_ID - pay for item
    - SEND:UUID - send money to user
    - PERK:PERK_ID - apply perk
    """
    data = request.data.strip()

    if ":" not in data:
        # legacy format - just UUID for login
        user = await db_service.get_user_by_uuid(data.upper())
        if user:
            return {
                "type": "login",
                "data": {"player_uuid": data.upper(), "name": user["name"]}
            }
        raise HTTPException(status_code=400, detail="Invalid QR code")

    parts = data.split(":", 1)
    qr_type = parts[0].upper()
    qr_value = parts[1].strip()

    if qr_type == "LOGIN":
        user = await db_service.get_user_by_uuid(qr_value.upper())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "type": "login",
            "data": {
                "player_uuid": user["player_uuid"],
                "name": user["name"]
            }
        }

    elif qr_type == "PAY":
        item = await db_service.get_item_by_id(qr_value)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {
            "type": "pay",
            "data": item
        }

    elif qr_type == "SEND":
        user = await db_service.get_user_by_uuid(qr_value.upper())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "type": "send",
            "data": {
                "player_uuid": user["player_uuid"],
                "name": user["name"]
            }
        }

    elif qr_type == "PERK":
        perk = await db_service.get_perk_by_id(qr_value)
        if not perk:
            raise HTTPException(status_code=404, detail="Perk not found")
        return {
            "type": "perk",
            "data": perk
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown QR type: {qr_type}")
