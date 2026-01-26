"""Database service - replaces SheetsService."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import (
    User, Attribute, Item, ActiveEffect, Perk, UserPerk, Trader, Transaction,
    async_session
)
from models.base import now_local


class DatabaseService:
    """Database operations service."""

    async def get_session(self) -> AsyncSession:
        return async_session()

    # User methods
    async def get_user_by_telegram_id(self, user_id: int) -> Optional[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            return user.to_dict() if user else None

    async def get_user_by_uuid(self, player_uuid: str) -> Optional[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user = result.scalar_one_or_none()
            return user.to_dict() if user else None

    async def create_user(self, user_id: int, name: str) -> dict:
        player_uuid = str(uuid.uuid4())[:8].upper()
        default_attrs = await self._get_default_attributes()

        async with async_session() as session:
            user = User(
                telegram_id=user_id,
                player_uuid=player_uuid,
                name=name,
                balance=100,
                attributes=default_attrs,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user.to_dict()

    async def _get_default_attributes(self) -> dict:
        try:
            config = await self.get_attribute_config()
            return {
                attr["attribute_name"]: int(attr.get("max_value", 10)) // 2
                for attr in config
            }
        except Exception:
            return {
                "strength": 5,
                "perception": 5,
                "endurance": 5,
                "charisma": 5,
                "intelligence": 5,
                "agility": 5,
                "luck": 5,
            }

    async def update_balance(self, player_uuid: str, new_balance: int) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user = result.scalar_one_or_none()
            if user:
                user.balance = new_balance
                await session.commit()
                return True
            return False

    async def link_telegram_to_player(self, telegram_id: int, player_uuid: str) -> bool:
        async with async_session() as session:
            # clear existing link
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            old_user = result.scalar_one_or_none()
            if old_user:
                old_user.telegram_id = None

            # link to new player
            result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user = result.scalar_one_or_none()
            if user:
                user.telegram_id = telegram_id
                await session.commit()
                return True
            return False

    async def unlink_telegram(self, telegram_id: int) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.telegram_id = None
                await session.commit()
                return True
            return False

    async def get_attribute_config(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(Attribute))
            return [attr.to_dict() for attr in result.scalars().all()]

    async def get_user_stats(self, player_uuid: str) -> Optional[dict]:
        user = await self.get_user_by_uuid(player_uuid)
        if not user:
            return None

        config = await self.get_attribute_config()
        attributes = []

        # attributes should be dict from JSONB column
        user_attrs = user.get("attributes") or {}

        # get active effects for temporary bonuses
        active_effects = await self.get_user_active_effects(player_uuid)
        effect_bonuses = {}
        for effect in active_effects:
            if effect["effect_type"].startswith("attr_"):
                attr_name = effect["effect_type"][5:]
                effect_bonuses[attr_name] = effect_bonuses.get(attr_name, 0) + effect["effect_value"]

        for attr_config in config:
            attr_name = attr_config["attribute_name"]
            base_value = user_attrs.get(attr_name)
            if base_value is None:
                base_value = 0
            bonus = effect_bonuses.get(attr_name, 0)
            attributes.append({
                "name": attr_name,
                "display_name": attr_config.get("display_name", attr_name),
                "value": base_value + bonus,
                "base_value": base_value,
                "bonus": bonus,
                "max_value": int(attr_config.get("max_value", 10)),
                "description": attr_config.get("description", ""),
            })

        return {
            "player_uuid": user["player_uuid"],
            "name": user["name"],
            "profession": user.get("profession", ""),
            "band": user.get("band", ""),
            "attributes": attributes,
            "active_effects": active_effects,
        }

    async def _update_user_attributes(self, player_uuid: str, attributes: dict) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user = result.scalar_one_or_none()
            if user:
                user.attributes = attributes
                await session.commit()
                return True
            return False

    # Items methods
    async def get_item_by_id(self, item_id: str) -> Optional[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Item).options(selectinload(Item.trader)).where(Item.item_id == item_id)
            )
            item = result.scalar_one_or_none()
            return item.to_dict() if item else None

    async def get_all_items(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Item).options(selectinload(Item.trader))
            )
            return [item.to_dict() for item in result.scalars().all()]

    # Active effects methods
    async def has_active_effect(self, player_uuid: str, item_id: str) -> bool:
        """Check if user has active effect from this item."""
        async with async_session() as session:
            now = now_local()
            result = await session.execute(
                select(ActiveEffect)
                .join(User)
                .join(Item)
                .where(User.player_uuid == player_uuid)
                .where(Item.item_id == item_id)
                .where(ActiveEffect.expires_at > now)
            )
            return result.scalar_one_or_none() is not None

    async def apply_item_effect(self, player_uuid: str, item_id: str) -> bool:
        """Apply temporary effect from item. Returns True if effect was applied."""
        async with async_session() as session:
            user_result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return False

            item_result = await session.execute(
                select(Item).where(Item.item_id == item_id)
            )
            item = item_result.scalar_one_or_none()
            if not item or not item.effect_type or not item.effect_duration:
                return False

            now = now_local()
            # check for existing active effect
            existing = await session.execute(
                select(ActiveEffect)
                .where(ActiveEffect.user_id == user.id)
                .where(ActiveEffect.item_id == item.id)
                .where(ActiveEffect.expires_at > now)
            )
            if existing.scalar_one_or_none():
                return False

            # create new active effect
            expires_at = now + timedelta(minutes=item.effect_duration)
            effect = ActiveEffect(
                user_id=user.id,
                item_id=item.id,
                effect_type=item.effect_type,
                effect_value=item.effect_value or 0,
                expires_at=expires_at
            )
            session.add(effect)
            await session.commit()
            return True

    async def get_user_active_effects(self, player_uuid: str) -> list[dict]:
        """Get all active effects for user."""
        async with async_session() as session:
            now = now_local()
            result = await session.execute(
                select(ActiveEffect)
                .options(selectinload(ActiveEffect.item))
                .join(User)
                .where(User.player_uuid == player_uuid)
                .where(ActiveEffect.expires_at > now)
            )
            effects = []
            for effect in result.scalars().all():
                effects.append({
                    "item_name": effect.item.name,
                    "effect_type": effect.effect_type,
                    "effect_value": effect.effect_value,
                    "expires_at": effect.expires_at.isoformat(),
                })
            return effects

    # Perks methods
    async def get_perk_by_id(self, perk_id: str) -> Optional[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Perk).where(Perk.perk_id == perk_id)
            )
            perk = result.scalar_one_or_none()
            return perk.to_dict() if perk else None

    async def get_all_perks(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(Perk))
            return [perk.to_dict() for perk in result.scalars().all()]

    async def has_user_perk(self, player_uuid: str, perk_id: str) -> bool:
        """Check if specific user has this perk."""
        async with async_session() as session:
            result = await session.execute(
                select(UserPerk)
                .join(User)
                .join(Perk)
                .where(User.player_uuid == player_uuid)
                .where(Perk.perk_id == perk_id)
            )
            return result.scalar_one_or_none() is not None

    async def is_perk_taken(self, perk_id: str) -> bool:
        """Check if any user has this perk (for unique perks)."""
        async with async_session() as session:
            result = await session.execute(
                select(UserPerk)
                .join(Perk)
                .where(Perk.perk_id == perk_id)
            )
            return result.scalar_one_or_none() is not None

    async def apply_perk(self, player_uuid: str, perk_id: str) -> tuple[bool, str]:
        """Apply perk to user. Returns (success, error_message)."""
        perk = await self.get_perk_by_id(perk_id)
        if not perk:
            return False, "perk_not_found"

        # check if user already has this perk
        if await self.has_user_perk(player_uuid, perk_id):
            return False, "already_applied"

        # check if unique perk is taken by anyone
        if perk.get("one_time") and await self.is_perk_taken(perk_id):
            return False, "perk_taken"

        user = await self.get_user_by_uuid(player_uuid)
        if not user:
            return False, "user_not_found"

        async with async_session() as session:
            # get user and perk objects
            user_result = await session.execute(
                select(User).where(User.player_uuid == player_uuid)
            )
            user_obj = user_result.scalar_one()

            perk_result = await session.execute(
                select(Perk).where(Perk.perk_id == perk_id)
            )
            perk_obj = perk_result.scalar_one()

            # apply effect
            effect_type = perk.get("effect_type", "")
            effect_value = int(perk.get("effect_value", 0))

            if effect_type.startswith("attr_"):
                attr_name = effect_type[5:]
                attrs = dict(user_obj.attributes or {})
                attrs[attr_name] = attrs.get(attr_name, 0) + effect_value
                user_obj.attributes = attrs
            elif effect_type == "balance":
                user_obj.balance += effect_value

            # record perk application
            user_perk = UserPerk(
                user_id=user_obj.id,
                perk_id=perk_obj.id,
            )
            session.add(user_perk)
            await session.commit()

        return True, ""

    async def get_user_perks(self, player_uuid: str) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(UserPerk)
                .options(selectinload(UserPerk.perk))
                .join(User)
                .where(User.player_uuid == player_uuid)
            )
            perks = []
            for user_perk in result.scalars().all():
                perk_dict = user_perk.perk.to_dict()
                perk_dict["applied_at"] = user_perk.applied_at.isoformat()
                perks.append(perk_dict)
            return perks

    # Traders methods
    async def get_trader_by_id(self, trader_id: str) -> Optional[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Trader).where(Trader.trader_id == trader_id)
            )
            trader = result.scalar_one_or_none()
            return trader.to_dict() if trader else None

    async def get_all_traders(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(Trader))
            return [trader.to_dict() for trader in result.scalars().all()]

    async def update_trader_balance(self, trader_id: str, new_balance: int) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(Trader).where(Trader.trader_id == trader_id)
            )
            trader = result.scalar_one_or_none()
            if trader:
                trader.balance = new_balance
                await session.commit()
                return True
            return False

    # Transactions methods
    async def log_transaction(
        self,
        from_type: str,
        from_id: str,
        to_type: str,
        to_id: str,
        amount: int,
        tx_type: str,
        description: str = ""
    ) -> bool:
        async with async_session() as session:
            tx = Transaction(
                from_type=from_type,
                from_id=from_id,
                to_type=to_type,
                to_id=to_id,
                amount=amount,
                tx_type=tx_type,
                description=description,
            )
            session.add(tx)
            await session.commit()
            return True

    async def get_transactions(self, limit: int = 100) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Transaction).order_by(desc(Transaction.timestamp)).limit(limit)
            )
            return [tx.to_dict() for tx in result.scalars().all()]

    async def get_user_transactions(self, player_uuid: str, limit: int = 50) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(Transaction)
                .where(
                    (Transaction.from_id == player_uuid) |
                    (Transaction.to_id == player_uuid)
                )
                .order_by(desc(Transaction.timestamp))
                .limit(limit)
            )
            return [tx.to_dict() for tx in result.scalars().all()]

    async def update_entity_image(self, entity_type: str, entity_id: str, image_url: str) -> bool:
        async with async_session() as session:
            if entity_type == "item":
                result = await session.execute(
                    select(Item).where(Item.item_id == entity_id)
                )
                entity = result.scalar_one_or_none()
            elif entity_type == "perk":
                result = await session.execute(
                    select(Perk).where(Perk.perk_id == entity_id)
                )
                entity = result.scalar_one_or_none()
            else:
                return False

            if entity:
                entity.image_url = image_url
                await session.commit()
                return True
            return False

    # Admin methods for getting all users
    async def get_all_users(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(User))
            return [
                {"player_uuid": u.player_uuid, "name": u.name}
                for u in result.scalars().all()
            ]


db_service = DatabaseService()
