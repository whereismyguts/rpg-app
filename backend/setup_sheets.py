#!/usr/bin/env python3
"""Setup Google Sheets with headers, default attributes, and test users."""

import json
from services.sheets import sheets_service


def setup_users_sheet():
    """Add headers to Users sheet."""
    print("Setting up Users sheet...")
    sheet = sheets_service.get_users_sheet()

    headers = [
        "user_id",
        "player_uuid",
        "name",
        "profession",
        "balance",
        "band",
        "attributes_json"
    ]

    # Check if headers already exist
    existing = sheet.row_values(1)
    if existing == headers:
        print("  Headers already exist, skipping.")
        return

    # Clear and set headers
    sheet.update(values=[headers], range_name="A1:G1")
    print(f"  Added headers: {headers}")


def setup_attributes_sheet():
    """Add headers and default SPECIAL attributes."""
    print("Setting up Attributes sheet...")
    sheet = sheets_service.get_attributes_sheet()

    headers = ["attribute_name", "display_name", "max_value", "description"]

    attributes = [
        ["strength", "Strength", 10, "Physical power and carrying capacity"],
        ["perception", "Perception", 10, "Environmental awareness and accuracy"],
        ["endurance", "Endurance", 10, "Health and resistance to damage"],
        ["charisma", "Charisma", 10, "Speech and barter effectiveness"],
        ["intelligence", "Intelligence", 10, "Skill points and dialogue options"],
        ["agility", "Agility", 10, "Action points and sneaking ability"],
        ["luck", "Luck", 10, "Critical chance and random encounters"],
    ]

    # Check if data exists
    existing = sheet.get_all_values()
    if len(existing) > 1:
        print(f"  Sheet already has {len(existing)-1} attributes, skipping.")
        return

    # Set headers + attributes
    data = [headers] + attributes
    sheet.update(values=data, range_name=f"A1:D{len(data)}")
    print(f"  Added {len(attributes)} attributes")


def create_test_users():
    """Create 2 test users."""
    print("Creating test users...")
    sheet = sheets_service.get_users_sheet()

    # Get attribute config for default values
    attrs_sheet = sheets_service.get_attributes_sheet()
    attr_config = attrs_sheet.get_all_records()

    default_attrs = {
        attr["attribute_name"]: int(attr.get("max_value", 10)) // 2
        for attr in attr_config
    }

    # Check existing users
    existing = sheet.get_all_records()
    existing_uuids = [r.get("player_uuid") for r in existing]

    test_users = [
        {
            "user_id": 100000001,
            "player_uuid": "TEST0001",
            "name": "Vault Dweller",
            "profession": "Wanderer",
            "balance": 500,
            "band": "Vault 101",
            "attributes": default_attrs,
        },
        {
            "user_id": 100000002,
            "player_uuid": "TEST0002",
            "name": "Lone Survivor",
            "profession": "Soldier",
            "balance": 250,
            "band": "Minutemen",
            "attributes": {**default_attrs, "strength": 7, "endurance": 7, "charisma": 3},
        },
    ]

    added = 0
    for user in test_users:
        if user["player_uuid"] in existing_uuids:
            print(f"  User {user['player_uuid']} already exists, skipping.")
            continue

        row = [
            user["user_id"],
            user["player_uuid"],
            user["name"],
            user["profession"],
            user["balance"],
            user["band"],
            json.dumps(user["attributes"]),
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        print(f"  Created user: {user['name']} ({user['player_uuid']})")
        added += 1

    print(f"  Added {added} test users")


def main():
    print("=" * 50)
    print("GOOGLE SHEETS SETUP")
    print("=" * 50)

    try:
        setup_users_sheet()
        setup_attributes_sheet()
        create_test_users()

        print("\n" + "=" * 50)
        print("SETUP COMPLETE!")
        print("=" * 50)

        # Show summary
        users_sheet = sheets_service.get_users_sheet()
        attrs_sheet = sheets_service.get_attributes_sheet()

        users = users_sheet.get_all_records()
        attrs = attrs_sheet.get_all_records()

        print(f"\nUsers: {len(users)}")
        for u in users:
            print(f"  - {u['name']} ({u['player_uuid']}) - {u['balance']} caps")

        print(f"\nAttributes: {len(attrs)}")
        for a in attrs:
            print(f"  - {a['display_name']} (max: {a['max_value']})")

    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
