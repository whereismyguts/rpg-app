"""Admin API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.settings import settings
from services.database import db_service
from services.imagegen import generate_image

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
    users = await db_service.get_all_users()
    return {"users": users}


@router.get("/items")
async def get_all_items():
    """Get all items for admin."""
    items = await db_service.get_all_items()
    return {"items": items}


@router.get("/perks")
async def get_all_perks():
    """Get all perks for admin."""
    perks = await db_service.get_all_perks()
    return {"perks": perks}


@router.get("/traders")
async def get_all_traders():
    """Get all traders for admin."""
    traders = await db_service.get_all_traders()
    return {"traders": traders}


@router.get("/transactions")
async def get_transactions(limit: int = 100):
    """Get recent transactions."""
    transactions = await db_service.get_transactions(limit)
    return {"transactions": transactions}


class GenerateImageRequest(BaseModel):
    entity_type: str  # "item" or "perk"
    entity_id: str
    prompt: str


@router.post("/generate-image")
async def generate_entity_image(request: GenerateImageRequest):
    """Generate image for item or perk and save URL to database."""
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    # verify entity exists
    if request.entity_type == "item":
        entity = await db_service.get_item_by_id(request.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Item not found")
    elif request.entity_type == "perk":
        entity = await db_service.get_perk_by_id(request.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Perk not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid entity type")

    # generate image
    image_url = await generate_image(request.prompt)
    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to generate image")

    # save URL to database
    success = await db_service.update_entity_image(
        request.entity_type,
        request.entity_id,
        image_url
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to save image URL")

    return {
        "success": True,
        "image_url": image_url
    }
