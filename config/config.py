import json
from pathlib import Path


class Config:
    SETTINGS_FILE = Path(__file__).parent / "settings.json"

    @classmethod
    def load_settings(cls):
        if not cls.SETTINGS_FILE.exists():
            raise FileNotFoundError(
                f"Settings file not found: {cls.SETTINGS_FILE}"
            )

        with open(cls.SETTINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)