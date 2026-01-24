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
    column_list = [User.id, User.player_uuid, User.name, User.telegram_id, User.balance, User.profession, User.band]
    column_searchable_list = [User.name, User.player_uuid]
    column_sortable_list = [User.id, User.name, User.balance]
    column_default_sort = [(User.id, True)]
    form_excluded_columns = [User.user_perks, User.created_at]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class AttributeAdmin(ModelView, model=Attribute):
    column_list = [Attribute.id, Attribute.attribute_name, Attribute.display_name, Attribute.max_value]
    column_searchable_list = [Attribute.attribute_name, Attribute.display_name]
    name = "Attribute"
    name_plural = "Attributes"
    icon = "fa-solid fa-chart-bar"


class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.item_id, Item.name, Item.price, Item.trader, Item.image_url]
    column_searchable_list = [Item.name, Item.item_id]
    column_sortable_list = [Item.id, Item.name, Item.price]
    name = "Item"
    name_plural = "Items"
    icon = "fa-solid fa-box"


class PerkAdmin(ModelView, model=Perk):
    column_list = [Perk.id, Perk.perk_id, Perk.name, Perk.one_time, Perk.effect_type, Perk.effect_value, Perk.image_url]
    column_searchable_list = [Perk.name, Perk.perk_id]
    form_excluded_columns = [Perk.user_perks]
    name = "Perk"
    name_plural = "Perks"
    icon = "fa-solid fa-star"


class UserPerkAdmin(ModelView, model=UserPerk):
    column_list = [UserPerk.id, UserPerk.user, UserPerk.perk, UserPerk.applied_at]
    column_sortable_list = [UserPerk.id, UserPerk.applied_at]
    column_default_sort = [(UserPerk.applied_at, True)]
    name = "User Perk"
    name_plural = "User Perks"
    icon = "fa-solid fa-user-plus"


class TraderAdmin(ModelView, model=Trader):
    column_list = [Trader.id, Trader.trader_id, Trader.name, Trader.balance]
    column_searchable_list = [Trader.name, Trader.trader_id]
    form_excluded_columns = [Trader.items]
    name = "Trader"
    name_plural = "Traders"
    icon = "fa-solid fa-store"


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.id, Transaction.timestamp, Transaction.tx_type, Transaction.from_type, Transaction.from_id, Transaction.to_type, Transaction.to_id, Transaction.amount]
    column_sortable_list = [Transaction.id, Transaction.timestamp, Transaction.amount]
    column_default_sort = [(Transaction.timestamp, True)]
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
    )

    admin.add_view(UserAdmin)
    admin.add_view(AttributeAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(PerkAdmin)
    admin.add_view(UserPerkAdmin)
    admin.add_view(TraderAdmin)
    admin.add_view(TransactionAdmin)

    return admin
