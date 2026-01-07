import json
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Telegram
    bot_token: str
    webapp_url: str = ""

    # Google Sheets
    google_sheet_id: str
    google_credentials_json: str = ""
    google_credentials_file: str = ""

    # Security
    password_enabled: bool = False
    app_password: str = ""
    secret_key: str = "change-me-in-production"

    # App
    log_level: str = "INFO"

    @property
    def google_credentials(self) -> dict:
        """Load Google credentials from JSON string or file."""
        # Option 1: JSON string in environment variable
        if self.google_credentials_json:
            return json.loads(self.google_credentials_json)

        # Get project root (parent of backend/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Option 2: Path to JSON file (try relative and absolute)
        if self.google_credentials_file:
            # Try as-is first
            if os.path.exists(self.google_credentials_file):
                with open(self.google_credentials_file, "r") as f:
                    return json.load(f)
            # Try relative to project root
            full_path = os.path.join(project_root, self.google_credentials_file)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    return json.load(f)

        # Option 3: Default paths
        default_paths = [
            os.path.join(project_root, "credentials", "service_account.json"),
            "credentials/service_account.json",
            "../credentials/service_account.json",
        ]
        for path in default_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)

        raise ValueError(
            "Google credentials not found. Set GOOGLE_CREDENTIALS_JSON or "
            "GOOGLE_CREDENTIALS_FILE, or place service_account.json in credentials/"
        )

    class Config:
        env_file = "../.env", ".env"  # Look in parent dir first, then current
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
