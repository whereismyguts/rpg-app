"""SQLAdmin panel configuration with enhanced UX."""

import uuid
from markupsafe import Markup
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import TextAreaField, SelectField, IntegerField, Form
from wtforms.validators import Optional, NumberRange
import json


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


# effect type choices for perks
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

from config.settings import settings
from models import User, Attribute, Item, Perk, UserPerk, Trader, Transaction
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

    column_list = ["id", "qr_code", "player_uuid", "name", "balance", "profession", "band", "telegram_id"]
    column_searchable_list = ["name", "player_uuid", "profession", "band"]
    column_sortable_list = ["id", "name", "balance", "created_at"]
    column_default_sort = [("id", True)]

    column_labels = {
        "id": "ID",
        "qr_code": "QR",
        "player_uuid": "UUID",
        "name": "Имя",
        "balance": "Баланс",
        "profession": "Профессия",
        "band": "Группировка",
        "telegram_id": "Telegram ID",
        "created_at": "Создан",
    }

    form_excluded_columns = ["user_perks", "created_at", "attributes"]

    # explicitly list form columns including extra fields
    form_columns = [
        "telegram_id",
        "player_uuid",
        "name",
        "profession",
        "balance",
        "band",
        "attr_strength",
        "attr_perception",
        "attr_endurance",
        "attr_charisma",
        "attr_intelligence",
        "attr_agility",
        "attr_luck",
    ]

    form_args = {
        "player_uuid": {"default": generate_uuid},
        "balance": {"default": 100},
    }

    form_widget_args = {
        "player_uuid": {"style": "text-transform: uppercase;"},
    }

    form_extra_fields = {
        "attr_strength": IntegerField("💪 Сила"),
        "attr_perception": IntegerField("👁 Восприятие"),
        "attr_endurance": IntegerField("❤️ Выносливость"),
        "attr_charisma": IntegerField("🗣 Харизма"),
        "attr_intelligence": IntegerField("🧠 Интеллект"),
        "attr_agility": IntegerField("🏃 Ловкость"),
        "attr_luck": IntegerField("🍀 Удача"),
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

        # collect attributes from extra fields
        attrs = {}
        for key in ["strength", "perception", "endurance", "charisma", "intelligence", "agility", "luck"]:
            field_name = f"attr_{key}"
            val = data.pop(field_name, None)
            if val is not None:
                attrs[key] = int(val)
        if attrs:
            data["attributes"] = attrs

    async def edit_form(self, obj):
        form = await super().edit_form(obj)
        if obj and obj.attributes:
            attrs = obj.attributes
            if isinstance(attrs, str):
                try:
                    attrs = json.loads(attrs)
                except:
                    attrs = {}
            if isinstance(attrs, dict):
                for key in ["strength", "perception", "endurance", "charisma", "intelligence", "agility", "luck"]:
                    field_name = f"attr_{key}"
                    if hasattr(form, field_name):
                        getattr(form, field_name).data = attrs.get(key)
        return form


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

    column_list = ["id", "qr_code", "image", "item_id", "name", "price", "trader", "description"]
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
        "trader": "Торговец",
        "description": "Описание",
        "image_url": "URL картинки",
    }

    form_args = {
        "item_id": {"default": lambda: f"ITEM_{generate_uuid()}"},
        "price": {"default": 10},
    }

    form_widget_args = {
        "description": {"rows": 3},
        "item_id": {"style": "text-transform: uppercase;"},
    }

    column_formatters = {
        "qr_code": lambda m, a: format_qr("PAY", m.item_id),
        "image": lambda m, a: format_image(m.image_url),
        "price": lambda m, a: format_balance(m.price),
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


def setup_admin(app):
    """Setup SQLAdmin with all models."""
    authentication_backend = AdminAuth(secret_key=settings.secret_key)

    admin = Admin(
        app,
        sync_engine,
        authentication_backend=authentication_backend,
        title="RPG Admin",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(PerkAdmin)
    admin.add_view(TraderAdmin)
    admin.add_view(UserPerkAdmin)
    admin.add_view(TransactionAdmin)
    admin.add_view(AttributeAdmin)

    return admin
