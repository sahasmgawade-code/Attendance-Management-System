import json
import shutil
from pathlib import Path


class Config:
    SETTINGS_FILE = Path(__file__).parent / "settings.json"
    DEFAULT_FILE = Path(__file__).parent / "settings.default.json"

    @classmethod
    def load_settings(cls):
        if not cls.SETTINGS_FILE.exists():
            if cls.DEFAULT_FILE.exists():
                shutil.copy2(cls.DEFAULT_FILE, cls.SETTINGS_FILE)
            else:
                raise FileNotFoundError(
                    f"Settings file not found: {cls.SETTINGS_FILE}"
                )

        with open(cls.SETTINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    @classmethod
    def get_date_format(cls):
        settings = cls.load_settings()
        return settings.get("date_format", "%d-%m-%Y")