"""SQLAdmin panel configuration with enhanced UX."""

import uuid
from markupsafe import Markup
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import TextAreaField, SelectField, IntegerField, Form
from wtforms.validators import Optional, NumberRange
import csv
import io
import json
from sqlalchemy import select


# SPECIAL attributes
SPECIAL_ATTRIBUTES = [
    ("strength", "💪 Сила"),
    ("perception", "👁 Восприятие"),
    ("endurance", "❤️ Выносливость"),
    ("charisma", "🗣 Харизма"),
    ("intelligence", "🧠 Интеллект"),
    ("agility", "🏃 Ловкость"),
    ("luck", "🍀 Удача"),
]


# effect type choices for perks (includes balance)
EFFECT_TYPE_CHOICES = [
    ("", "-- Выберите --"),
    ("balance", "💰 Баланс (крышки)"),
    ("attr_strength", "💪 Сила"),
    ("attr_perception", "👁 Восприятие"),
    ("attr_endurance", "❤️ Выносливость"),
    ("attr_charisma", "🗣 Харизма"),
    ("attr_intelligence", "🧠 Интеллект"),
    ("attr_agility", "🏃 Ловкость"),
    ("attr_luck", "🍀 Удача"),
]

# effect type choices for items (only attributes, no balance)
ITEM_EFFECT_TYPE_CHOICES = [
    ("", "-- Выберите --"),
    ("attr_strength", "💪 Сила"),
    ("attr_perception", "👁 Восприятие"),
    ("attr_endurance", "❤️ Выносливость"),
    ("attr_charisma", "🗣 Харизма"),
    ("attr_intelligence", "🧠 Интеллект"),
    ("attr_agility", "🏃 Ловкость"),
    ("attr_luck", "🍀 Удача"),
]

from config.settings import settings
from models import User, Attribute, Item, ActiveEffect, Perk, UserPerk, Trader, Transaction
from models.base import sync_engine


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        password = form.get("password")
        if password == settings.admin_password:
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)


def generate_uuid():
    """Generate 8-char uppercase UUID."""
    return str(uuid.uuid4())[:8].upper()


def format_image(url):
    """Format image URL as thumbnail."""
    if url:
        return Markup(f'<img src="{url}" style="max-width:60px;max-height:60px;border-radius:4px;" />')
    return "-"


def format_qr(entity_type, entity_id):
    """Format QR code image."""
    if entity_id:
        qr_data = f"{entity_type}:{entity_id}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=80x80&data={qr_data}"
        return Markup(f'<img src="{qr_url}" style="width:60px;height:60px;" title="{qr_data}" />')
    return "-"


def format_balance(value):
    """Format balance with caps icon."""
    return Markup(f'<strong>{value}</strong> 🔴')


class UserAdmin(ModelView, model=User):
    name = "Игрок"
    name_plural = "Игроки"
    icon = "fa-solid fa-user"

    column_list = ["id", "qr_code", "player_uuid", "name", "hp", "balance", "profession", "band", "telegram_id"]
    column_searchable_list = ["name", "player_uuid", "profession", "band"]
    column_sortable_list = ["id", "name", "hp", "balance", "created_at"]
    column_default_sort = [("id", True)]

    column_labels = {
        "id": "ID",
        "qr_code": "QR",
        "player_uuid": "UUID",
        "name": "Имя",
        "hp": "HP",
        "balance": "Баланс",
        "profession": "Профессия",
        "band": "Группировка",
        "telegram_id": "Telegram ID",
        "attributes": "S.P.E.C.I.A.L.",
        "created_at": "Создан",
    }

    form_excluded_columns = ["user_perks", "active_effects", "created_at"]

    form_args = {
        "player_uuid": {"default": generate_uuid},
        "balance": {"default": 100},
        "hp": {"default": 100},
    }

    form_widget_args = {
        "player_uuid": {"style": "text-transform: uppercase;"},
    }

    column_formatters = {
        "qr_code": lambda m, a: format_qr("LOGIN", m.player_uuid),
        "balance": lambda m, a: format_balance(m.balance),
    }

    async def on_model_change(self, data, model, is_created, request):
        if is_created and not data.get("player_uuid"):
            data["player_uuid"] = generate_uuid()
        if data.get("player_uuid"):
            data["player_uuid"] = data["player_uuid"].upper()
        # parse attributes from string to dict if needed
        attrs = data.get("attributes")
        if isinstance(attrs, str):
            import ast
            data["attributes"] = ast.literal_eval(attrs)


class AttributeAdmin(ModelView, model=Attribute):
    name = "Атрибут"
    name_plural = "Атрибуты"
    icon = "fa-solid fa-chart-bar"

    column_list = ["id", "attribute_name", "display_name", "max_value", "description"]
    column_searchable_list = ["attribute_name", "display_name"]

    column_labels = {
        "id": "ID",
        "attribute_name": "Имя (код)",
        "display_name": "Отображение",
        "max_value": "Макс. значение",
        "description": "Описание",
    }


class ItemAdmin(ModelView, model=Item):
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-box"

    column_list = ["id", "qr_code", "image", "item_id", "name", "price", "hp_restore", "trader", "effect_type", "effect_duration", "description"]
    column_searchable_list = ["name", "item_id", "description"]
    column_sortable_list = ["id", "name", "price"]
    column_default_sort = [("name", False)]

    column_labels = {
        "id": "ID",
        "qr_code": "QR",
        "image": "Картинка",
        "item_id": "ID товара",
        "name": "Название",
        "price": "Цена",
        "hp_restore": "❤️ HP",
        "trader": "Торговец",
        "description": "Описание",
        "image_url": "URL картинки",
        "effect_type": "Тип эффекта",
        "effect_value": "Значение",
        "effect_duration": "Длительность (мин)",
    }

    form_overrides = {
        "effect_type": SelectField,
    }

    form_args = {
        "item_id": {"default": lambda: f"ITEM_{generate_uuid()}"},
        "price": {"default": 10},
        "effect_type": {"choices": ITEM_EFFECT_TYPE_CHOICES, "coerce": str},
    }

    form_widget_args = {
        "description": {"rows": 3},
        "item_id": {"style": "text-transform: uppercase;"},
    }

    column_formatters = {
        "qr_code": lambda m, a: format_qr("PAY", m.item_id),
        "image": lambda m, a: format_image(m.image_url),
        "price": lambda m, a: format_balance(m.price),
        "effect_duration": lambda m, a: f"{m.effect_duration} мин" if m.effect_duration else "-",
    }

    async def on_model_change(self, data, model, is_created, request):
        if is_created and not data.get("item_id"):
            data["item_id"] = f"ITEM_{generate_uuid()}"
        if data.get("item_id"):
            data["item_id"] = data["item_id"].upper()


class PerkAdmin(ModelView, model=Perk):
    name = "Перк"
    name_plural = "Перки"
    icon = "fa-solid fa-star"

    column_list = ["id", "qr_code", "image", "perk_id", "name", "one_time", "effect_type", "effect_value", "description"]
    column_searchable_list = ["name", "perk_id", "description"]
    column_sortable_list = ["id", "name", "one_time"]

    column_labels = {
        "id": "ID",
        "qr_code": "QR",
        "image": "Картинка",
        "perk_id": "ID перка",
        "name": "Название",
        "description": "Описание",
        "one_time": "Одноразовый",
        "effect_type": "Тип эффекта",
        "effect_value": "Значение",
        "image_url": "URL картинки",
    }

    form_excluded_columns = ["user_perks"]

    form_overrides = {
        "effect_type": SelectField,
    }

    form_args = {
        "perk_id": {"default": lambda: f"PERK_{generate_uuid()}"},
        "effect_value": {"default": 1},
        "effect_type": {"choices": EFFECT_TYPE_CHOICES, "coerce": str},
    }

    form_widget_args = {
        "description": {"rows": 3},
        "perk_id": {"style": "text-transform: uppercase;"},
    }

    column_formatters = {
        "qr_code": lambda m, a: format_qr("PERK", m.perk_id),
        "image": lambda m, a: format_image(m.image_url),
        "one_time": lambda m, a: "✅ Да" if m.one_time else "🔄 Нет",
        "effect_value": lambda m, a: Markup(f'<span style="color:{"green" if (m.effect_value or 0) > 0 else "red"}">{"+" if (m.effect_value or 0) > 0 else ""}{m.effect_value or 0}</span>'),
    }

    async def on_model_change(self, data, model, is_created, request):
        if is_created and not data.get("perk_id"):
            data["perk_id"] = f"PERK_{generate_uuid()}"
        if data.get("perk_id"):
            data["perk_id"] = data["perk_id"].upper()


class UserPerkAdmin(ModelView, model=UserPerk):
    name = "Перк игрока"
    name_plural = "Перки игроков"
    icon = "fa-solid fa-user-plus"

    column_list = ["id", "user", "perk", "applied_at"]
    column_sortable_list = ["id", "applied_at"]
    column_default_sort = [("applied_at", True)]

    column_labels = {
        "id": "ID",
        "user": "Игрок",
        "perk": "Перк",
        "applied_at": "Применён",
    }


class ActiveEffectAdmin(ModelView, model=ActiveEffect):
    name = "Активный эффект"
    name_plural = "Активные эффекты"
    icon = "fa-solid fa-hourglass-half"

    column_list = ["id", "user", "item", "effect_type", "effect_value", "applied_at", "expires_at"]
    column_sortable_list = ["id", "applied_at", "expires_at"]
    column_default_sort = [("expires_at", True)]

    column_labels = {
        "id": "ID",
        "user": "Игрок",
        "item": "Товар",
        "effect_type": "Тип эффекта",
        "effect_value": "Значение",
        "applied_at": "Применён",
        "expires_at": "Истекает",
    }


class TraderAdmin(ModelView, model=Trader):
    name = "Торговец"
    name_plural = "Торговцы"
    icon = "fa-solid fa-store"

    column_list = ["id", "trader_id", "name", "balance"]
    column_searchable_list = ["name", "trader_id"]
    column_sortable_list = ["id", "name", "balance"]

    column_labels = {
        "id": "ID",
        "trader_id": "ID торговца",
        "name": "Имя",
        "balance": "Баланс",
        "items": "Товары",
    }

    form_excluded_columns = ["items"]

    form_args = {
        "trader_id": {"default": lambda: f"TRADER_{generate_uuid()}"},
        "balance": {"default": 0},
    }

    form_widget_args = {
        "trader_id": {"style": "text-transform: uppercase;"},
    }

    column_formatters = {
        "balance": lambda m, a: format_balance(m.balance),
    }

    async def on_model_change(self, data, model, is_created, request):
        if is_created and not data.get("trader_id"):
            data["trader_id"] = f"TRADER_{generate_uuid()}"
        if data.get("trader_id"):
            data["trader_id"] = data["trader_id"].upper()


class TransactionAdmin(ModelView, model=Transaction):
    name = "Транзакция"
    name_plural = "Транзакции"
    icon = "fa-solid fa-exchange-alt"

    column_list = ["id", "timestamp", "tx_type", "from_type", "from_id", "to_type", "to_id", "amount", "description"]
    column_sortable_list = ["id", "timestamp", "amount", "tx_type"]
    column_default_sort = [("timestamp", True)]

    column_labels = {
        "id": "ID",
        "timestamp": "Время",
        "tx_type": "Тип",
        "from_type": "Откуда (тип)",
        "from_id": "Откуда (ID)",
        "to_type": "Куда (тип)",
        "to_id": "Куда (ID)",
        "amount": "Сумма",
        "description": "Описание",
    }

    can_create = False
    can_edit = False
    can_delete = False

    column_formatters = {
        "amount": lambda m, a: format_balance(m.amount) if m.amount else "-",
        "tx_type": lambda m, a: {
            "transfer": "💸 Перевод",
            "purchase": "🛒 Покупка",
            "perk": "⭐ Перк",
            "login": "🔐 Вход",
        }.get(m.tx_type, m.tx_type),
    }


from sqladmin import BaseView, expose


class PrintQRView(BaseView):
    name = "Печать QR"
    icon = "fa-solid fa-qrcode"

    @expose("/print-qr", methods=["GET"])
    async def print_qr_page(self, request: Request):
        from models.base import async_session
        async with async_session() as session:
            result = await session.execute(select(User).order_by(User.name))
            users = result.scalars().all()

        return await self.templates.TemplateResponse(
            request,
            "print_qr.html",
            context={"users": users},
        )


class ImportView(BaseView):
    name = "Импорт"
    icon = "fa-solid fa-file-import"

    @expose("/import", methods=["GET", "POST"])
    async def import_page(self, request: Request):
        message = None
        message_type = None

        if request.method == "POST":
            form = await request.form()
            import_type = form.get("import_type")
            file = form.get("file")

            if file and file.filename:
                content = await file.read()
                try:
                    # parse JSON or CSV
                    if file.filename.endswith(".csv"):
                        text = content.decode("utf-8")
                        reader = csv.DictReader(io.StringIO(text))
                        data = []
                        for row in reader:
                            # convert types
                            clean_row = {}
                            for k, v in row.items():
                                if v == "" or v is None:
                                    clean_row[k] = None
                                elif k in ("price", "effect_value", "effect_duration"):
                                    clean_row[k] = int(v) if v else None
                                elif k == "one_time":
                                    clean_row[k] = v.lower() in ("true", "1", "yes")
                                else:
                                    clean_row[k] = v
                            data.append(clean_row)
                    else:
                        data = json.loads(content)
                        if not isinstance(data, list):
                            raise ValueError("JSON must be array")

                    from models import async_session as get_session
                    from sqlalchemy.ext.asyncio import AsyncSession

                    created = 0
                    updated = 0

                    async with get_session() as session:
                        if import_type == "items":
                            # get trader mapping
                            traders_result = await session.execute(select(Trader))
                            traders = {t.trader_id: t.id for t in traders_result.scalars().all()}

                            for item_data in data:
                                item_id = item_data.get("item_id")
                                if not item_id:
                                    continue

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

                        elif import_type == "perks":
                            for perk_data in data:
                                perk_id = perk_data.get("perk_id")
                                if not perk_id:
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

                        elif import_type == "users":
                            for user_data in data:
                                name = user_data.get("name")
                                if not name:
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
                                    player_uuid = existing.player_uuid if existing else generate_uuid()
                                else:
                                    player_uuid = player_uuid.upper()

                                # build attributes dict
                                attributes = user_data.get("attributes", {})
                                if not attributes:
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

                        await session.commit()

                    message = f"Импорт завершён: создано {created}, обновлено {updated}"
                    message_type = "success"

                except json.JSONDecodeError:
                    message = "Ошибка: неверный формат JSON"
                    message_type = "error"
                except Exception as e:
                    message = f"Ошибка: {str(e)}"
                    message_type = "error"
            else:
                message = "Выберите файл"
                message_type = "error"

        return await self.templates.TemplateResponse(
            request,
            "import.html",
            context={"message": message, "message_type": message_type},
        )


def setup_admin(app):
    """Setup SQLAdmin with all models."""
    authentication_backend = AdminAuth(secret_key=settings.secret_key)

    admin = Admin(
        app,
        sync_engine,
        authentication_backend=authentication_backend,
        title="RPG Admin",
        base_url="/admin",
        templates_dir="templates/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(PerkAdmin)
    admin.add_view(TraderAdmin)
    admin.add_view(UserPerkAdmin)
    admin.add_view(ActiveEffectAdmin)
    admin.add_view(TransactionAdmin)
    admin.add_view(AttributeAdmin)
    admin.add_view(PrintQRView)
    admin.add_view(ImportView)

    return admin
