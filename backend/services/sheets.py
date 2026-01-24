import json
import uuid
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings


class SheetsService:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self):
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None

    def _get_client(self) -> gspread.Client:
        if self._client is None:
            creds = Credentials.from_service_account_info(
                settings.google_credentials,
                scopes=self.SCOPES,
            )
            self._client = gspread.authorize(creds)
        return self._client

    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        if self._spreadsheet is None:
            client = self._get_client()
            self._spreadsheet = client.open_by_key(settings.google_sheet_id)
        return self._spreadsheet

    def get_users_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Users")

    def get_attributes_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Attributes")

    def get_items_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Items")

    def get_perks_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Perks")

    def get_user_perks_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("UserPerks")

    def get_traders_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Traders")

    def get_transactions_sheet(self) -> gspread.Worksheet:
        return self._get_spreadsheet().worksheet("Transactions")

    def get_user_by_telegram_id(self, user_id: int) -> Optional[dict]:
        sheet = self.get_users_sheet()
        records = sheet.get_all_records()
        for record in records:
            if str(record.get("user_id")) == str(user_id):
                return self._parse_user(record)
        return None

    def get_user_by_uuid(self, player_uuid: str) -> Optional[dict]:
        sheet = self.get_users_sheet()
        records = sheet.get_all_records()
        for record in records:
            if record.get("player_uuid") == player_uuid:
                return self._parse_user(record)
        return None

    def _parse_user(self, record: dict) -> dict:
        """Parse user record and convert attributes_json to dict."""
        user = dict(record)
        if user.get("attributes_json"):
            try:
                user["attributes"] = json.loads(user["attributes_json"])
            except json.JSONDecodeError:
                user["attributes"] = {}
        else:
            user["attributes"] = {}
        return user

    def create_user(self, user_id: int, name: str) -> dict:
        sheet = self.get_users_sheet()
        player_uuid = str(uuid.uuid4())[:8].upper()

        # Get default attributes from config
        default_attrs = self._get_default_attributes()

        row = [
            user_id,
            player_uuid,
            name,
            "",  # profession
            100,  # starting balance
            "",  # band
            json.dumps(default_attrs),
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

        return {
            "user_id": user_id,
            "player_uuid": player_uuid,
            "name": name,
            "profession": "",
            "balance": 100,
            "band": "",
            "attributes": default_attrs,
        }

    def _get_default_attributes(self) -> dict:
        """Get default attribute values from config sheet."""
        try:
            config = self.get_attribute_config()
            return {
                attr["attribute_name"]: int(attr.get("max_value", 10)) // 2
                for attr in config
            }
        except Exception:
            # Fallback to classic SPECIAL
            return {
                "strength": 5,
                "perception": 5,
                "endurance": 5,
                "charisma": 5,
                "intelligence": 5,
                "agility": 5,
                "luck": 5,
            }

    def update_balance(self, player_uuid: str, new_balance: int) -> bool:
        sheet = self.get_users_sheet()
        try:
            cell = sheet.find(player_uuid)
            if cell:
                # Balance is in column E (index 5)
                sheet.update_cell(cell.row, 5, new_balance)
                return True
        except Exception:
            pass
        return False

    def link_telegram_to_player(self, telegram_id: int, player_uuid: str) -> bool:
        """Link a telegram user to a player. Clears previous links."""
        sheet = self.get_users_sheet()
        try:
            # First, clear any existing link for this telegram_id
            records = sheet.get_all_records()
            for i, record in enumerate(records):
                if str(record.get("user_id")) == str(telegram_id):
                    # Clear this link (row index is i+2 because of header)
                    sheet.update_cell(i + 2, 1, "")

            # Now link to the new player
            cell = sheet.find(player_uuid)
            if cell:
                # user_id is in column A (index 1)
                sheet.update_cell(cell.row, 1, telegram_id)
                return True
        except Exception:
            pass
        return False

    def unlink_telegram(self, telegram_id: int) -> bool:
        """Unlink a telegram user from their current player."""
        sheet = self.get_users_sheet()
        try:
            records = sheet.get_all_records()
            for i, record in enumerate(records):
                if str(record.get("user_id")) == str(telegram_id):
                    # Clear this link (row index is i+2 because of header)
                    sheet.update_cell(i + 2, 1, "")
                    return True
        except Exception:
            pass
        return False

    def get_attribute_config(self) -> list[dict]:
        sheet = self.get_attributes_sheet()
        return sheet.get_all_records()

    def get_user_stats(self, player_uuid: str) -> Optional[dict]:
        """Get user attributes with full config info."""
        user = self.get_user_by_uuid(player_uuid)
        if not user:
            return None

        config = self.get_attribute_config()
        attributes = []

        for attr_config in config:
            attr_name = attr_config["attribute_name"]
            value = user.get("attributes", {}).get(attr_name, 0)
            attributes.append({
                "name": attr_name,
                "display_name": attr_config.get("display_name", attr_name),
                "value": value,
                "max_value": int(attr_config.get("max_value", 10)),
                "description": attr_config.get("description", ""),
            })

        return {
            "player_uuid": user["player_uuid"],
            "name": user["name"],
            "profession": user.get("profession", ""),
            "band": user.get("band", ""),
            "attributes": attributes,
        }


    # Items methods
    def get_item_by_id(self, item_id: str) -> Optional[dict]:
        """Get item by its ID."""
        try:
            sheet = self.get_items_sheet()
            records = sheet.get_all_records()
            for record in records:
                if record.get("item_id") == item_id:
                    return dict(record)
        except Exception:
            pass
        return None

    def get_all_items(self) -> list[dict]:
        """Get all available items."""
        try:
            sheet = self.get_items_sheet()
            return sheet.get_all_records()
        except Exception:
            return []

    # Perks methods
    def get_perk_by_id(self, perk_id: str) -> Optional[dict]:
        """Get perk by its ID."""
        try:
            sheet = self.get_perks_sheet()
            records = sheet.get_all_records()
            for record in records:
                if record.get("perk_id") == perk_id:
                    return dict(record)
        except Exception:
            pass
        return None

    def get_all_perks(self) -> list[dict]:
        """Get all available perks."""
        try:
            sheet = self.get_perks_sheet()
            return sheet.get_all_records()
        except Exception:
            return []

    def has_user_perk(self, player_uuid: str, perk_id: str) -> bool:
        """Check if user already has this perk applied."""
        try:
            sheet = self.get_user_perks_sheet()
            records = sheet.get_all_records()
            for record in records:
                if record.get("player_uuid") == player_uuid and record.get("perk_id") == perk_id:
                    return True
        except Exception:
            pass
        return False

    def apply_perk(self, player_uuid: str, perk_id: str) -> bool:
        """Apply a perk to user. Returns False if one_time perk already applied."""
        perk = self.get_perk_by_id(perk_id)
        if not perk:
            return False

        # check if one_time perk already applied
        if perk.get("one_time") and self.has_user_perk(player_uuid, perk_id):
            return False

        user = self.get_user_by_uuid(player_uuid)
        if not user:
            return False

        # apply effect
        effect_type = perk.get("effect_type", "")
        effect_value = int(perk.get("effect_value", 0))

        if effect_type.startswith("attr_"):
            # modify attribute (e.g., attr_strength)
            attr_name = effect_type[5:]
            attrs = user.get("attributes", {})
            attrs[attr_name] = attrs.get(attr_name, 0) + effect_value
            self._update_user_attributes(player_uuid, attrs)
        elif effect_type == "balance":
            new_balance = user["balance"] + effect_value
            self.update_balance(player_uuid, new_balance)

        # record perk application
        try:
            from datetime import datetime
            sheet = self.get_user_perks_sheet()
            sheet.append_row([
                player_uuid,
                perk_id,
                datetime.now().isoformat()
            ], value_input_option="USER_ENTERED")
        except Exception:
            pass

        return True

    def _update_user_attributes(self, player_uuid: str, attributes: dict) -> bool:
        """Update user attributes JSON."""
        sheet = self.get_users_sheet()
        try:
            cell = sheet.find(player_uuid)
            if cell:
                # attributes_json is in column G (index 7)
                sheet.update_cell(cell.row, 7, json.dumps(attributes))
                return True
        except Exception:
            pass
        return False

    def get_user_perks(self, player_uuid: str) -> list[dict]:
        """Get all perks applied to user."""
        try:
            sheet = self.get_user_perks_sheet()
            records = sheet.get_all_records()
            user_perks = []
            for record in records:
                if record.get("player_uuid") == player_uuid:
                    perk = self.get_perk_by_id(record.get("perk_id"))
                    if perk:
                        perk["applied_at"] = record.get("applied_at")
                        user_perks.append(perk)
            return user_perks
        except Exception:
            return []

    # Traders methods
    def get_trader_by_id(self, trader_id: str) -> Optional[dict]:
        """Get trader by ID."""
        try:
            sheet = self.get_traders_sheet()
            records = sheet.get_all_records()
            for record in records:
                if record.get("trader_id") == trader_id:
                    return dict(record)
        except Exception:
            pass
        return None

    def get_all_traders(self) -> list[dict]:
        """Get all traders."""
        try:
            sheet = self.get_traders_sheet()
            return sheet.get_all_records()
        except Exception:
            return []

    def update_trader_balance(self, trader_id: str, new_balance: int) -> bool:
        """Update trader balance."""
        sheet = self.get_traders_sheet()
        try:
            cell = sheet.find(trader_id)
            if cell:
                # balance is in column C (index 3)
                sheet.update_cell(cell.row, 3, new_balance)
                return True
        except Exception:
            pass
        return False

    # Transactions methods
    def log_transaction(
        self,
        from_type: str,  # "player" or "trader" or "system"
        from_id: str,
        to_type: str,  # "player" or "trader"
        to_id: str,
        amount: int,
        tx_type: str,  # "transfer", "purchase", "perk"
        description: str = ""
    ) -> bool:
        """Log a transaction."""
        try:
            from datetime import datetime
            sheet = self.get_transactions_sheet()
            sheet.append_row([
                datetime.now().isoformat(),
                from_type,
                from_id,
                to_type,
                to_id,
                amount,
                tx_type,
                description
            ], value_input_option="USER_ENTERED")
            return True
        except Exception:
            return False

    def get_transactions(self, limit: int = 100) -> list[dict]:
        """Get recent transactions."""
        try:
            sheet = self.get_transactions_sheet()
            records = sheet.get_all_records()
            return records[-limit:] if len(records) > limit else records
        except Exception:
            return []

    def get_user_transactions(self, player_uuid: str, limit: int = 50) -> list[dict]:
        """Get transactions for a specific user."""
        try:
            sheet = self.get_transactions_sheet()
            records = sheet.get_all_records()
            user_txs = [
                r for r in records
                if r.get("from_id") == player_uuid or r.get("to_id") == player_uuid
            ]
            return user_txs[-limit:] if len(user_txs) > limit else user_txs
        except Exception:
            return []

    def update_entity_image(self, entity_type: str, entity_id: str, image_url: str) -> bool:
        """Update image_url for item or perk."""
        try:
            if entity_type == "item":
                sheet = self.get_items_sheet()
                id_col = "item_id"
            elif entity_type == "perk":
                sheet = self.get_perks_sheet()
                id_col = "perk_id"
            else:
                return False

            headers = sheet.row_values(1)

            # ensure image_url column exists
            if "image_url" not in headers:
                col = len(headers) + 1
                sheet.update_cell(1, col, "image_url")
                headers.append("image_url")

            image_col = headers.index("image_url") + 1

            # find entity row
            records = sheet.get_all_records()
            for i, record in enumerate(records):
                if record.get(id_col) == entity_id:
                    sheet.update_cell(i + 2, image_col, image_url)
                    return True

            return False
        except Exception as e:
            print(f"Update image error: {e}")
            return False


sheets_service = SheetsService()
