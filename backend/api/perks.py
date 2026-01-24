"""Perks API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.database import db_service

router = APIRouter()


class ApplyPerkRequest(BaseModel):
    player_uuid: str
    perk_id: str


@router.get("/")
async def get_all_perks():
    """Get all available perks."""
    perks = await db_service.get_all_perks()
    return {"perks": perks}


@router.get("/{perk_id}")
async def get_perk(perk_id: str):
    """Get perk by ID."""
    perk = await db_service.get_perk_by_id(perk_id)
    if not perk:
        raise HTTPException(status_code=404, detail="Perk not found")
    return perk


@router.get("/user/{player_uuid}")
async def get_user_perks(player_uuid: str):
    """Get all perks applied to user."""
    user = await db_service.get_user_by_uuid(player_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    perks = await db_service.get_user_perks(player_uuid)
    return {"perks": perks}


@router.post("/apply")
async def apply_perk(request: ApplyPerkRequest):
    """Apply a perk to user."""
    user = await db_service.get_user_by_uuid(request.player_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    perk = await db_service.get_perk_by_id(request.perk_id)
    if not perk:
        raise HTTPException(status_code=404, detail="Perk not found")

    # check if one_time and already applied
    if perk.get("one_time") and await db_service.has_user_perk(request.player_uuid, request.perk_id):
        raise HTTPException(status_code=400, detail="Perk already applied")

    success = await db_service.apply_perk(request.player_uuid, request.perk_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply perk")

    # log perk transaction
    await db_service.log_transaction(
        from_type="system",
        from_id="PERK",
        to_type="player",
        to_id=request.player_uuid,
        amount=0,
        tx_type="perk",
        description=f"Перк: {perk.get('name', request.perk_id)}"
    )

    # get updated user stats
    updated_user = await db_service.get_user_by_uuid(request.player_uuid)

    return {
        "success": True,
        "perk": perk,
        "new_balance": updated_user["balance"],
        "new_attributes": updated_user.get("attributes", {})
    }
