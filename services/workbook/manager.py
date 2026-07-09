from pathlib import Path
import shutil
import json

from config.config import Config


class WorkbookManager:
    """
    Manages the registration and retrieval
    of the Master Workbook.
    """

    def __init__(self):
        self.settings_path = Config.SETTINGS_FILE
        self.settings = Config.load_settings()

    def get_registered_workbook(self):
        """
        Returns the registered workbook path.
        Returns None if no workbook is registered
        or if the file no longer exists on disk.
        """

        workbook = self.settings.get("master_workbook", "")

        if workbook and Path(workbook).exists():
            return Path(workbook)

        return None
    def workbook_exists(self):
        """
        Checks whether the registered workbook exists.
        """

        workbook = self.get_registered_workbook()

        if workbook is None:
            return False

        return workbook.exists()

    def register_workbook(self, source_path):
        """
        Copies the workbook into uploads/master
        and updates settings.json.
        """

        source_path = Path(source_path)

        destination_folder = Path("uploads/master")
        destination_folder.mkdir(parents=True, exist_ok=True)

        destination = destination_folder / source_path.name

        shutil.copy2(source_path, destination)

        # Store as a forward-slash path so settings.json stays
        # portable across Windows, Linux, and Mac
        self.settings["master_workbook"] = destination.as_posix()

        with open(self.settings_path, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=4)

        return destination