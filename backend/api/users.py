from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from services.database import db_service
from services.qr import generate_qr_code, generate_qr_image

router = APIRouter()


class UserResponse(BaseModel):
    player_uuid: str
    name: str
    balance: int
    hp: int = 100
    profession: str
    band: str


class DamageRequest(BaseModel):
    target_uuid: str
    amount: int = 1


class RespawnRequest(BaseModel):
    player_uuid: str


class AttributeItem(BaseModel):
    name: str
    display_name: str
    value: int
    base_value: int = 0
    bonus: int = 0
    max_value: int
    description: str


class ActiveEffectItem(BaseModel):
    item_name: str
    effect_type: str
    effect_value: int
    expires_at: str


class StatsResponse(BaseModel):
    player_uuid: str
    name: str
    profession: str
    role_description: str = ""
    band: str
    attributes: list[AttributeItem]
    active_effects: list[ActiveEffectItem] = []


class QRResponse(BaseModel):
    qr_base64: str


@router.get("/me", response_model=UserResponse)
async def get_current_user(player_uuid: str = Query(...)):
    user = await db_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    return UserResponse(
        player_uuid=user["player_uuid"],
        name=user["name"],
        balance=user["balance"],
        hp=user.get("hp", 100),
        profession=user.get("profession", ""),
        band=user.get("band", ""),
    )


@router.get("/stats", response_model=StatsResponse)
async def get_user_stats(player_uuid: str = Query(...)):
    stats = await db_service.get_user_stats(player_uuid.upper())
    if not stats:
        raise HTTPException(404, "User not found")

    return StatsResponse(**stats)


@router.get("/qr")
async def get_user_qr(player_uuid: str = Query(...), format: str = Query("base64")):
    """Get QR code for player UUID."""
    user = await db_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    if format == "image":
        image_bytes = generate_qr_image(player_uuid.upper())
        return Response(content=image_bytes, media_type="image/png")

    qr_base64 = generate_qr_code(player_uuid.upper())
    return QRResponse(qr_base64=qr_base64)


@router.get("/lookup", response_model=UserResponse)
async def lookup_user(player_uuid: str = Query(...)):
    """Look up a user by UUID (for transfers)."""
    user = await db_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    return UserResponse(
        player_uuid=user["player_uuid"],
        name=user["name"],
        balance=0,  # Don't expose balance in lookup
        profession=user.get("profession", ""),
        band=user.get("band", ""),
    )


@router.get("/transactions")
async def get_user_transactions(player_uuid: str = Query(...), limit: int = Query(50)):
    """Get user's transaction history."""
    user = await db_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    transactions = await db_service.get_user_transactions(player_uuid.upper(), limit)
    return {"transactions": transactions}


@router.post("/damage")
async def deal_damage(request: DamageRequest):
    """Deal damage to a player."""
    target = await db_service.get_user_by_uuid(request.target_uuid.upper())
    if not target:
        raise HTTPException(404, "Target not found")

    if target.get("hp", 100) <= 0:
        raise HTTPException(400, "Цель уже мертва")

    new_hp = await db_service.deal_damage(request.target_uuid.upper(), request.amount)

    await db_service.log_transaction(
        from_type="system",
        from_id="DAMAGE",
        to_type="player",
        to_id=request.target_uuid.upper(),
        amount=request.amount,
        tx_type="damage",
        description=f"Получено урона: {request.amount}"
    )

    return {
        "success": True,
        "target_uuid": request.target_uuid.upper(),
        "damage": request.amount,
        "new_hp": new_hp,
        "is_dead": new_hp <= 0
    }


@router.post("/respawn")
async def respawn_player(request: RespawnRequest):
    """Respawn a dead player - lose all perks/effects, restore with 5 HP."""
    user = await db_service.get_user_by_uuid(request.player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    if user.get("hp", 100) > 0:
        raise HTTPException(400, "Игрок ещё жив")

    await db_service.respawn_player(request.player_uuid.upper())

    await db_service.log_transaction(
        from_type="system",
        from_id="RESPAWN",
        to_type="player",
        to_id=request.player_uuid.upper(),
        amount=0,
        tx_type="respawn",
        description="Возрождение"
    )

    return {
        "success": True,
        "new_hp": 5
    }
