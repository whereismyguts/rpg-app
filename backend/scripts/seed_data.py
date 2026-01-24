"""Seed database with test data."""

import asyncio
import sys
sys.path.insert(0, '/home/karmanov/projects/rpg-app/backend')

from models import async_session, init_db, User, Attribute, Item, Perk, Trader


async def seed():
    print("Initializing database...")
    await init_db()

    async with async_session() as session:
        # Check if data exists
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Data already exists, skipping seed.")
            return

        print("Seeding attributes...")
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

        print("Seeding traders...")
        traders = [
            Trader(trader_id="TRADER1", name="Торговец Иван", balance=1000),
            Trader(trader_id="TRADER2", name="Торговец Мария", balance=500),
        ]
        session.add_all(traders)
        await session.flush()

        print("Seeding items...")
        items = [
            Item(item_id="STIMPAK", name="Стимпак", description="Восстанавливает здоровье", price=25, trader_id=traders[0].id),
            Item(item_id="RADAWAY", name="Рад-Авэй", description="Выводит радиацию", price=30, trader_id=traders[0].id),
            Item(item_id="NUKA_COLA", name="Ядер-Кола", description="Утоляет жажду", price=15, trader_id=traders[1].id),
            Item(item_id="MENTATS", name="Ментаты", description="+2 Интеллект на время", price=50, trader_id=traders[1].id),
        ]
        session.add_all(items)

        print("Seeding perks...")
        perks = [
            Perk(perk_id="STRONG_BACK", name="Крепкая спина", description="+2 к переносимому весу", one_time=True, effect_type="attr_strength", effect_value=2),
            Perk(perk_id="NIGHT_PERSON", name="Сова", description="+1 Восприятие ночью", one_time=True, effect_type="attr_perception", effect_value=1),
            Perk(perk_id="FORTUNE_FINDER", name="Искатель удачи", description="+50 крышек", one_time=False, effect_type="balance", effect_value=50),
        ]
        session.add_all(perks)

        print("Seeding test users...")
        users = [
            User(player_uuid="LEGION1", name="Легионер", balance=100, profession="Воин", attributes={"strength": 7, "perception": 5, "endurance": 6, "charisma": 3, "intelligence": 4, "agility": 5, "luck": 5}),
            User(player_uuid="TRADER01", name="Бродяга", balance=200, profession="Торговец", attributes={"strength": 4, "perception": 6, "endurance": 5, "charisma": 7, "intelligence": 5, "agility": 4, "luck": 4}),
            User(player_uuid="VAULT101", name="Обитатель Убежища", balance=150, profession="Инженер", attributes={"strength": 4, "perception": 5, "endurance": 4, "charisma": 5, "intelligence": 8, "agility": 5, "luck": 4}),
        ]
        session.add_all(users)

        await session.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
