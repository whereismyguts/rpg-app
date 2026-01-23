"""Seed Google Sheets with initial data."""

import sys
sys.path.insert(0, '/home/karmanov/projects/rpg-app/backend')

import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Data to seed
USERS_DATA = [
    ["user_id", "player_uuid", "name", "profession", "balance", "band", "attributes_json"],
    ["", "VAULT001", "Джон Митчелл", "Доктор", 500, "Vault Dwellers", '{"strength":4,"perception":7,"endurance":5,"charisma":6,"intelligence":9,"agility":5,"luck":4}'],
    ["", "VAULT002", "Мария Санчес", "Торговец", 1200, "Караванщики", '{"strength":3,"perception":6,"endurance":4,"charisma":8,"intelligence":7,"agility":5,"luck":7}'],
    ["", "NCR001", "Рейнджер Крейг", "Рейнджер", 350, "NCR", '{"strength":7,"perception":8,"endurance":7,"charisma":4,"intelligence":5,"agility":7,"luck":2}'],
    ["", "GHOUL01", "Рауль Техада", "Механик", 800, "Гули", '{"strength":5,"perception":4,"endurance":9,"charisma":3,"intelligence":8,"agility":4,"luck":7}'],
    ["", "LEGION1", "Вульпес Инкульта", "Фрументарий", 450, "Легион", '{"strength":6,"perception":7,"endurance":6,"charisma":7,"intelligence":8,"agility":6,"luck":3}'],
    ["", "BOS001", "Паладин Рамос", "Паладин", 600, "Братство Стали", '{"strength":8,"perception":5,"endurance":8,"charisma":3,"intelligence":6,"agility":5,"luck":5}'],
    ["", "WASTE01", "Дикарь Джек", "Охотник", 150, "Пустошь", '{"strength":6,"perception":8,"endurance":6,"charisma":2,"intelligence":4,"agility":8,"luck":6}'],
    ["", "STRIP01", "Мистер Хаус", "Магнат", 9999, "Нью-Вегас", '{"strength":1,"perception":6,"endurance":1,"charisma":9,"intelligence":10,"agility":1,"luck":8}'],
]

ITEMS_DATA = [
    ["item_id", "name", "description", "price", "image_url"],
    ["WATER01", "Очищенная вода", "Чистая вода без радиации. Восстанавливает здоровье.", 20, ""],
    ["NUKACOLA", "Нука-Кола", "Легендарный напиток довоенной эпохи. Слегка радиоактивен.", 25, ""],
    ["NUKAQUANT", "Нука-Кола Квантум", "Светится в темноте! Редкий коллекционный напиток.", 100, ""],
    ["STIMPAK", "Стимулятор", "Автоматический инъектор с лекарством. Мгновенное исцеление.", 75, ""],
    ["RADAWAY", "Антирадин", "Выводит радиацию из организма. Необходим в Пустоши.", 50, ""],
    ["IGUANA", "Игуана на палочке", "Питательное мясо игуаны. Возможно, не только игуаны.", 15, ""],
    ["FANCY01", "Причудливые закуски", "Довоенные снеки в идеальном состоянии. 200 лет свежести!", 35, ""],
    ["BEER01", "Пиво", "Тёплое пустошное пиво. Лучше, чем ничего.", 10, ""],
    ["WHISKEY", "Виски", "Крепкий алкоголь. Снимает стресс, снижает точность.", 30, ""],
    ["SUNSET", "Сансет Сарсапарилла", "Газировка со вкусом корневого пива. Собирай крышки!", 20, ""],
]

PERKS_DATA = [
    ["perk_id", "name", "description", "effect_type", "effect_value", "one_time"],
    ["INTENSE", "Интенсивная тренировка", "Тяжёлые тренировки в пустоши закалили твоё тело.", "attr_strength", 1, "TRUE"],
    ["SNIPER", "Глаз снайпера", "Твой взгляд стал острее. Ничто не ускользнёт от тебя.", "attr_perception", 1, "TRUE"],
    ["SURVIVAL", "Выживший", "Пустошь не смогла тебя сломить. Ты стал выносливее.", "attr_endurance", 1, "TRUE"],
    ["SMOOTH", "Гладкий оператор", "Люди охотнее прислушиваются к тебе.", "attr_charisma", 1, "TRUE"],
    ["EDUCATED", "Образованный", "Нашёл старые книги в убежище. Знания - сила!", "attr_intelligence", 1, "TRUE"],
    ["NINJA", "Ниндзя пустоши", "Быстрый как ветер, тихий как тень.", "attr_agility", 1, "TRUE"],
    ["FORTUNE", "Колесо фортуны", "Удача улыбнулась тебе сегодня!", "attr_luck", 2, "TRUE"],
    ["CAPS100", "Тайник с крышками", "Ты нашёл спрятанный тайник!", "balance", 100, "TRUE"],
    ["CAPS250", "Клад караванщика", "Заброшенный караван принёс находку!", "balance", 250, "TRUE"],
    ["JACKPOT", "Джекпот!", "Сорвал куш в казино Нью-Вегаса!", "balance", 500, "TRUE"],
]

ATTRIBUTES_DATA = [
    ["attribute_name", "display_name", "max_value", "description"],
    ["strength", "Сила", 10, "Физическая мощь. Влияет на урон в ближнем бою и переносимый вес."],
    ["perception", "Восприятие", 10, "Осведомлённость об окружении. Влияет на точность и обнаружение врагов."],
    ["endurance", "Выносливость", 10, "Физическая стойкость. Влияет на здоровье и сопротивление."],
    ["charisma", "Харизма", 10, "Обаяние и лидерские качества. Влияет на цены и диалоги."],
    ["intelligence", "Интеллект", 10, "Умственные способности. Влияет на навыки и опыт."],
    ["agility", "Ловкость", 10, "Координация и рефлексы. Влияет на скорость и скрытность."],
    ["luck", "Удача", 10, "Влияет на критические удары и случайные события."],
]

USER_PERKS_DATA = [
    ["player_uuid", "perk_id", "applied_at"],
]


def main():
    print("Connecting to Google Sheets...")
    creds = Credentials.from_service_account_info(
        settings.google_credentials,
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(settings.google_sheet_id)

    print(f"Connected to: {spreadsheet.title}")

    # Create or update sheets
    sheets_data = {
        "Users": USERS_DATA,
        "Attributes": ATTRIBUTES_DATA,
        "Items": ITEMS_DATA,
        "Perks": PERKS_DATA,
        "UserPerks": USER_PERKS_DATA,
    }

    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]

    for sheet_name, data in sheets_data.items():
        print(f"\nProcessing {sheet_name}...")

        if sheet_name in existing_sheets:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Clear existing data
            worksheet.clear()
            print(f"  Cleared existing {sheet_name}")
        else:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
            print(f"  Created new sheet {sheet_name}")

        # Write data
        if data:
            worksheet.update(data, value_input_option="USER_ENTERED")
            print(f"  Written {len(data)-1} rows to {sheet_name}")

    print("\n✓ All data seeded successfully!")


if __name__ == "__main__":
    main()
