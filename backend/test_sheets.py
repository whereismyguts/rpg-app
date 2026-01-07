#!/usr/bin/env python3
"""Test Google Sheets connection and configuration."""

import sys
import json

def test_settings():
    print("=" * 50)
    print("1. TESTING SETTINGS")
    print("=" * 50)

    try:
        from config.settings import settings
        print(f"[OK] Settings loaded")
        print(f"    - BOT_TOKEN: {'*' * 10}...{settings.bot_token[-5:]}" if settings.bot_token else "    - BOT_TOKEN: NOT SET")
        print(f"    - GOOGLE_SHEET_ID: {settings.google_sheet_id[:20]}..." if settings.google_sheet_id else "    - GOOGLE_SHEET_ID: NOT SET")
        print(f"    - PASSWORD_ENABLED: {settings.password_enabled}")
        print(f"    - WEBAPP_URL: {settings.webapp_url or 'NOT SET'}")
        return True
    except Exception as e:
        print(f"[FAIL] Settings error: {e}")
        return False


def test_credentials():
    print("\n" + "=" * 50)
    print("2. TESTING GOOGLE CREDENTIALS")
    print("=" * 50)

    try:
        from config.settings import settings
        creds = settings.google_credentials
        print(f"[OK] Credentials loaded")
        print(f"    - Type: {creds.get('type', 'unknown')}")
        print(f"    - Project ID: {creds.get('project_id', 'unknown')}")
        print(f"    - Client Email: {creds.get('client_email', 'unknown')}")
        return True
    except Exception as e:
        print(f"[FAIL] Credentials error: {e}")
        return False


def test_sheets_connection():
    print("\n" + "=" * 50)
    print("3. TESTING SHEETS CONNECTION")
    print("=" * 50)

    try:
        from services.sheets import sheets_service
        spreadsheet = sheets_service._get_spreadsheet()
        print(f"[OK] Connected to spreadsheet")
        print(f"    - Title: {spreadsheet.title}")
        print(f"    - URL: {spreadsheet.url}")
        return True
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False


def test_users_sheet():
    print("\n" + "=" * 50)
    print("4. TESTING USERS WORKSHEET")
    print("=" * 50)

    try:
        from services.sheets import sheets_service
        sheet = sheets_service.get_users_sheet()
        headers = sheet.row_values(1)
        expected = ["user_id", "player_uuid", "name", "profession", "balance", "band", "attributes_json"]

        print(f"[OK] Users worksheet found")
        print(f"    - Headers: {headers}")

        if headers == expected:
            print(f"[OK] Headers match expected structure")
        else:
            print(f"[WARN] Headers differ from expected: {expected}")

        records = sheet.get_all_records()
        print(f"    - Rows: {len(records)}")
        return True
    except Exception as e:
        print(f"[FAIL] Users sheet error: {e}")
        return False


def test_attributes_sheet():
    print("\n" + "=" * 50)
    print("5. TESTING ATTRIBUTES WORKSHEET")
    print("=" * 50)

    try:
        from services.sheets import sheets_service
        sheet = sheets_service.get_attributes_sheet()
        headers = sheet.row_values(1)
        expected = ["attribute_name", "display_name", "max_value", "description"]

        print(f"[OK] Attributes worksheet found")
        print(f"    - Headers: {headers}")

        if headers == expected:
            print(f"[OK] Headers match expected structure")
        else:
            print(f"[WARN] Headers differ from expected: {expected}")

        records = sheet.get_all_records()
        print(f"    - Attributes defined: {len(records)}")

        if records:
            print(f"    - Attributes: {[r.get('attribute_name') for r in records]}")
        else:
            print(f"[WARN] No attributes defined! Add rows to Attributes sheet.")

        return True
    except Exception as e:
        print(f"[FAIL] Attributes sheet error: {e}")
        return False


def test_bot_token():
    print("\n" + "=" * 50)
    print("6. TESTING TELEGRAM BOT TOKEN")
    print("=" * 50)

    try:
        import httpx
        from config.settings import settings

        response = httpx.get(f"https://api.telegram.org/bot{settings.bot_token}/getMe")
        data = response.json()

        if data.get("ok"):
            bot = data["result"]
            print(f"[OK] Bot token valid")
            print(f"    - Username: @{bot.get('username')}")
            print(f"    - Name: {bot.get('first_name')}")
            print(f"    - Bot ID: {bot.get('id')}")
            return True
        else:
            print(f"[FAIL] Invalid token: {data.get('description')}")
            return False
    except Exception as e:
        print(f"[FAIL] Bot token error: {e}")
        return False


def main():
    print("\n" + "#" * 50)
    print("# RPG-APP CONFIGURATION TEST")
    print("#" * 50)

    results = []
    results.append(("Settings", test_settings()))
    results.append(("Credentials", test_credentials()))
    results.append(("Sheets Connection", test_sheets_connection()))
    results.append(("Users Worksheet", test_users_sheet()))
    results.append(("Attributes Worksheet", test_attributes_sheet()))
    results.append(("Telegram Bot", test_bot_token()))

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED! Ready to run.")
    else:
        print("SOME TESTS FAILED. Check errors above.")
    print("=" * 50 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
