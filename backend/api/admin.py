"""Admin API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.settings import settings
from services.sheets import sheets_service

router = APIRouter()


class VerifyRequest(BaseModel):
    password: str


@router.post("/verify")
async def verify_admin_password(request: VerifyRequest):
    """Verify admin password for QR generator access."""
    if request.password == settings.admin_password:
        return {"success": True}
    raise HTTPException(status_code=401, detail="Неверный пароль")


@router.get("/users")
async def get_all_users():
    """Get all users for admin."""
    sheet = sheets_service.get_users_sheet()
    records = sheet.get_all_records()
    return {
        "users": [
            {
                "player_uuid": r.get("player_uuid"),
                "name": r.get("name"),
            }
            for r in records if r.get("player_uuid")
        ]
    }


@router.get("/items")
async def get_all_items():
    """Get all items for admin."""
    items = sheets_service.get_all_items()
    return {"items": items}


@router.get("/perks")
async def get_all_perks():
    """Get all perks for admin."""
    perks = sheets_service.get_all_perks()
    return {"perks": perks}
