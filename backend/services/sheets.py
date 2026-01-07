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

    def update_balance(self, player_uuid: str, new_balance: float) -> bool:
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


sheets_service = SheetsService()
