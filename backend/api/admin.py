"""Admin API endpoints."""

import base64
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from services.database import db_service
from services.imagegen import generate_image, upload_to_catbox
from models import async_session, Attribute, Trader, Item, Perk, User
from sqlalchemy import select

router = APIRouter()


class VerifyRequest(BaseModel):
    password: str


@router.post("/verify")
async def verify_admin_password(request: VerifyRequest):
    """Verify admin password for QR generator access."""
    if request.password == settings.admin_password:
        return {"success": True}
    raise HTTPException(status_code=401, detail="Неверный пароль")


@router.post("/seed")
async def seed_database(request: VerifyRequest):
    """Seed database with initial data. Requires admin password."""
    if request.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    async with async_session() as session:
        # check if data exists
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            return {"success": False, "message": "Data already exists"}

        # seed attributes
        attributes = [
            Attribute(attribute_name="strength", display_name="СИЛА", max_value=10, description="Физическая сила"),
            Attribute(attribute_name="perception", display_name="ВОСПРИЯТИЕ", max_value=10, description="Внимательность"),
            Attribute(attribute_name="endurance", display_name="ВЫНОСЛИВОСТЬ", max_value=10, description="Стойкость"),
            Attribute(attribute_name="charisma", display_name="ХАРИЗМА", max_value=10, description="Обаяние"),
            Attribute(attribute_name="intelligence", display_name="ИНТЕЛЛЕКТ", max_value=10, description="Умственные способности"),
            Attribute(attribute_name="agility", display_name="ЛОВКОСТЬ", max_value=10, description="Скорость и гибкость"),
            Attribute(attribute_name="luck", display_name="УДАЧА", max_value=10, description="Везение"),
        ]
        session.add_all(attributes)

        # seed traders
        traders = [
            Trader(trader_id="TRADER1", name="Торговец Иван", balance=1000),
            Trader(trader_id="TRADER2", name="Торговец Мария", balance=500),
        ]
        session.add_all(traders)
        await session.flush()

        # seed items
        items = [
            Item(item_id="STIMPAK", name="Стимпак", description="Восстанавливает здоровье", price=25, trader_id=traders[0].id),
            Item(item_id="RADAWAY", name="Рад-Авэй", description="Выводит радиацию", price=30, trader_id=traders[0].id),
            Item(item_id="NUKA_COLA", name="Ядер-Кола", description="Утоляет жажду", price=15, trader_id=traders[1].id),
            Item(item_id="MENTATS", name="Ментаты", description="+2 Интеллект на время", price=50, trader_id=traders[1].id),
        ]
        session.add_all(items)

        # seed perks
        perks = [
            Perk(perk_id="STRONG_BACK", name="Крепкая спина", description="+2 к силе", one_time=True, effect_type="attr_strength", effect_value=2),
            Perk(perk_id="NIGHT_PERSON", name="Сова", description="+1 Восприятие", one_time=True, effect_type="attr_perception", effect_value=1),
            Perk(perk_id="FORTUNE_FINDER", name="Искатель удачи", description="+50 крышек", one_time=False, effect_type="balance", effect_value=50),
        ]
        session.add_all(perks)

        # seed test users
        users = [
            User(player_uuid="LEGION1", name="Легионер", balance=100, profession="Воин", attributes={"strength": 7, "perception": 5, "endurance": 6, "charisma": 3, "intelligence": 4, "agility": 5, "luck": 5}),
            User(player_uuid="TRADER01", name="Бродяга", balance=200, profession="Торговец", attributes={"strength": 4, "perception": 6, "endurance": 5, "charisma": 7, "intelligence": 5, "agility": 4, "luck": 4}),
            User(player_uuid="VAULT101", name="Обитатель Убежища", balance=150, profession="Инженер", attributes={"strength": 4, "perception": 5, "endurance": 4, "charisma": 5, "intelligence": 8, "agility": 5, "luck": 4}),
        ]
        session.add_all(users)

        await session.commit()

    return {"success": True, "message": "Database seeded with test data"}


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


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image file and return hosted URL."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # read file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # upload to catbox
    url = await upload_to_catbox(content)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    return {"success": True, "url": url}


class Base64ImageRequest(BaseModel):
    image_data: str  # base64 encoded image or data URL
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


@router.post("/upload-image-base64")
async def upload_image_base64(request: Base64ImageRequest):
    """Upload base64 image and optionally save to entity."""
    data = request.image_data

    # handle data URL format
    if data.startswith("data:image"):
        # extract base64 part after comma
        if "," in data:
            data = data.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    # upload to catbox
    url = await upload_to_catbox(image_bytes)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    # if entity specified, save to database
    if request.entity_type and request.entity_id:
        success = await db_service.update_entity_image(
            request.entity_type,
            request.entity_id,
            url
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save image URL")

    return {"success": True, "url": url}


class SetImageUrlRequest(BaseModel):
    entity_type: str
    entity_id: str
    image_url: str


@router.post("/set-image-url")
async def set_image_url(request: SetImageUrlRequest):
    """Set image URL for an entity directly."""
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

    success = await db_service.update_entity_image(
        request.entity_type,
        request.entity_id,
        request.image_url
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to save image URL")

    return {"success": True, "url": request.image_url}
