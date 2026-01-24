"""SQLAdmin panel configuration."""

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

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


class UserAdmin(ModelView, model=User):
    column_list = ["id", "player_uuid", "name", "telegram_id", "balance", "profession", "band"]
    column_searchable_list = ["name", "player_uuid"]
    column_sortable_list = ["id", "name", "balance"]
    column_default_sort = [("id", True)]
    form_excluded_columns = ["user_perks", "created_at"]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class AttributeAdmin(ModelView, model=Attribute):
    column_list = ["id", "attribute_name", "display_name", "max_value"]
    column_searchable_list = ["attribute_name", "display_name"]
    name = "Attribute"
    name_plural = "Attributes"
    icon = "fa-solid fa-chart-bar"


class ItemAdmin(ModelView, model=Item):
    column_list = ["id", "item_id", "name", "price", "trader", "image_url"]
    column_searchable_list = ["name", "item_id"]
    column_sortable_list = ["id", "name", "price"]
    name = "Item"
    name_plural = "Items"
    icon = "fa-solid fa-box"


class PerkAdmin(ModelView, model=Perk):
    column_list = ["id", "perk_id", "name", "one_time", "effect_type", "effect_value", "image_url"]
    column_searchable_list = ["name", "perk_id"]
    form_excluded_columns = ["user_perks"]
    name = "Perk"
    name_plural = "Perks"
    icon = "fa-solid fa-star"


class UserPerkAdmin(ModelView, model=UserPerk):
    column_list = ["id", "user", "perk", "applied_at"]
    column_sortable_list = ["id", "applied_at"]
    column_default_sort = [("applied_at", True)]
    name = "User Perk"
    name_plural = "User Perks"
    icon = "fa-solid fa-user-plus"


class TraderAdmin(ModelView, model=Trader):
    column_list = ["id", "trader_id", "name", "balance"]
    column_searchable_list = ["name", "trader_id"]
    form_excluded_columns = ["items"]
    name = "Trader"
    name_plural = "Traders"
    icon = "fa-solid fa-store"


class TransactionAdmin(ModelView, model=Transaction):
    column_list = ["id", "timestamp", "tx_type", "from_type", "from_id", "to_type", "to_id", "amount"]
    column_sortable_list = ["id", "timestamp", "amount"]
    column_default_sort = [("timestamp", True)]
    can_create = False
    can_edit = False
    can_delete = False
    name = "Transaction"
    name_plural = "Transactions"
    icon = "fa-solid fa-exchange-alt"


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
    admin.add_view(AttributeAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(PerkAdmin)
    admin.add_view(UserPerkAdmin)
    admin.add_view(TraderAdmin)
    admin.add_view(TransactionAdmin)

    return admin
