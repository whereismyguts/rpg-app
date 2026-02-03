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


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    profession: Optional[str] = None
    band: Optional[str] = None
    balance: Optional[int] = None
    attributes: Optional[dict] = None


@router.get("/user/{player_uuid}")
async def get_user_details(player_uuid: str):
    """Get user details including attributes."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.player_uuid == player_uuid.upper())
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "player_uuid": user.player_uuid,
            "name": user.name,
            "profession": user.profession or "",
            "band": user.band or "",
            "balance": user.balance,
            "telegram_id": user.telegram_id,
            "attributes": user.attributes or {}
        }


@router.put("/user/{player_uuid}")
async def update_user(player_uuid: str, request: UpdateUserRequest):
    """Update user including attributes."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.player_uuid == player_uuid.upper())
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if request.name is not None:
            user.name = request.name
        if request.profession is not None:
            user.profession = request.profession
        if request.band is not None:
            user.band = request.band
        if request.balance is not None:
            user.balance = request.balance
        if request.attributes is not None:
            user.attributes = request.attributes

        await session.commit()
        return {"success": True}


@router.get("/attributes")
async def get_attribute_config():
    """Get attribute configuration."""
    config = await db_service.get_attribute_config()
    return {"attributes": config}


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


@router.post("/import/items")
async def import_items(file: UploadFile = File(...)):
    """Bulk import items from JSON file."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be JSON")

    import json
    content = await file.read()
    try:
        items_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(items_data, list):
        raise HTTPException(status_code=400, detail="JSON must be array of items")

    created = 0
    updated = 0
    errors = []

    async with async_session() as session:
        # get trader mapping
        traders_result = await session.execute(select(Trader))
        traders = {t.trader_id: t.id for t in traders_result.scalars().all()}

        for idx, item_data in enumerate(items_data):
            try:
                item_id = item_data.get("item_id")
                if not item_id:
                    errors.append(f"Row {idx}: missing item_id")
                    continue

                # check if exists
                result = await session.execute(
                    select(Item).where(Item.item_id == item_id)
                )
                existing = result.scalar_one_or_none()

                trader_db_id = None
                if item_data.get("trader_id"):
                    trader_db_id = traders.get(item_data["trader_id"])

                if existing:
                    existing.name = item_data.get("name", existing.name)
                    existing.description = item_data.get("description", existing.description)
                    existing.price = item_data.get("price", existing.price)
                    existing.trader_id = trader_db_id
                    existing.effect_type = item_data.get("effect_type")
                    existing.effect_value = item_data.get("effect_value")
                    existing.effect_duration = item_data.get("effect_duration")
                    updated += 1
                else:
                    item = Item(
                        item_id=item_id,
                        name=item_data.get("name", item_id),
                        description=item_data.get("description"),
                        price=item_data.get("price", 0),
                        trader_id=trader_db_id,
                        effect_type=item_data.get("effect_type"),
                        effect_value=item_data.get("effect_value"),
                        effect_duration=item_data.get("effect_duration"),
                    )
                    session.add(item)
                    created += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        await session.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/import/users")
async def import_users(file: UploadFile = File(...)):
    """Bulk import users from JSON file."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be JSON")

    import json
    content = await file.read()
    try:
        users_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(users_data, list):
        raise HTTPException(status_code=400, detail="JSON must be array of users")

    created = 0
    updated = 0
    errors = []

    async with async_session() as session:
        for idx, user_data in enumerate(users_data):
            try:
                name = user_data.get("name")
                if not name:
                    errors.append(f"Row {idx}: missing name")
                    continue
                name = name.strip()

                # find existing user by name
                result = await session.execute(
                    select(User).where(User.name == name)
                )
                existing = result.scalar_one_or_none()

                # use existing uuid or generate new one
                player_uuid = user_data.get("player_uuid")
                if not player_uuid:
                    import uuid as uuid_module
                    player_uuid = existing.player_uuid if existing else str(uuid_module.uuid4())[:8].upper()
                else:
                    player_uuid = player_uuid.upper()

                # build attributes dict
                attributes = user_data.get("attributes", {})
                if not attributes:
                    # try to build from individual fields
                    attr_fields = ["strength", "perception", "endurance", "charisma", "intelligence", "agility", "luck"]
                    for field in attr_fields:
                        if field in user_data:
                            attributes[field] = int(user_data[field])

                if existing:
                    existing.name = user_data.get("name", existing.name)
                    existing.profession = user_data.get("profession", existing.profession)
                    existing.role_description = user_data.get("role_description", existing.role_description)
                    existing.balance = user_data.get("balance", existing.balance)
                    existing.hp = user_data.get("hp", existing.hp)
                    existing.band = user_data.get("band", existing.band)
                    if attributes:
                        existing.attributes = attributes
                    updated += 1
                else:
                    user = User(
                        player_uuid=player_uuid,
                        name=name,
                        profession=user_data.get("profession"),
                        role_description=user_data.get("role_description"),
                        balance=user_data.get("balance", 100),
                        hp=user_data.get("hp", 100),
                        band=user_data.get("band"),
                        attributes=attributes if attributes else {
                            "strength": 5, "perception": 5, "endurance": 5,
                            "charisma": 5, "intelligence": 5, "agility": 5, "luck": 5
                        },
                    )
                    session.add(user)
                    created += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        await session.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/import/perks")
async def import_perks(file: UploadFile = File(...)):
    """Bulk import perks from JSON file."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be JSON")

    import json
    content = await file.read()
    try:
        perks_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(perks_data, list):
        raise HTTPException(status_code=400, detail="JSON must be array of perks")

    created = 0
    updated = 0
    errors = []

    async with async_session() as session:
        for idx, perk_data in enumerate(perks_data):
            try:
                perk_id = perk_data.get("perk_id")
                if not perk_id:
                    errors.append(f"Row {idx}: missing perk_id")
                    continue

                result = await session.execute(
                    select(Perk).where(Perk.perk_id == perk_id)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.name = perk_data.get("name", existing.name)
                    existing.description = perk_data.get("description", existing.description)
                    existing.one_time = perk_data.get("one_time", existing.one_time)
                    existing.effect_type = perk_data.get("effect_type")
                    existing.effect_value = perk_data.get("effect_value")
                    updated += 1
                else:
                    perk = Perk(
                        perk_id=perk_id,
                        name=perk_data.get("name", perk_id),
                        description=perk_data.get("description"),
                        one_time=perk_data.get("one_time", False),
                        effect_type=perk_data.get("effect_type"),
                        effect_value=perk_data.get("effect_value"),
                    )
                    session.add(perk)
                    created += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        await session.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }
