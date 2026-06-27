from openpyxl.workbook import Workbook

from config.config import Config
from models.validation import ValidationResult


class WorkbookValidator:
    """
    Validates the structure of the Master Workbook.
    """

    def __init__(self, workbook: Workbook):
        self.workbook = workbook
        self.settings = Config.load_settings()

    def validate_workbook(self) -> ValidationResult:
        """
        Validates workbook structure.

        Returns:
            ValidationResult
        """

        result = ValidationResult()

        student_sheet_name = self.settings["student_sheet"]
        attendance_sheet_name = self.settings["attendance_sheet"]

        # -----------------------------
        # Validate Required Worksheets
        # -----------------------------

        if student_sheet_name not in self.workbook.sheetnames:
            result.add_error(
                f"Missing worksheet: '{student_sheet_name}'"
            )

        if attendance_sheet_name not in self.workbook.sheetnames:
            result.add_error(
                f"Missing worksheet: '{attendance_sheet_name}'"
            )

        if not result.is_valid:
            return result

        # -----------------------------
        # Validate Student Details Sheet
        # -----------------------------

        student_sheet = self.workbook[student_sheet_name]

        student_headers = [
            cell.value for cell in student_sheet[1]
        ]

        required_student_headers = [
            "URN",
            "Student Name",
            "Student Email",
            "Student Phone",
            "Parent Phone",
            "Present Count",
            "Working Days",
            "Attendance %"
        ]

        for header in required_student_headers:

            if header not in student_headers:
                result.add_error(
                    f"Missing column '{header}' in Student Details sheet."
                )

        # -----------------------------
        # Validate Attendance Sheet
        # -----------------------------

        attendance_sheet = self.workbook[attendance_sheet_name]

        attendance_headers = [
            cell.value for cell in attendance_sheet[1]
        ]

        required_attendance_headers = [
            "URN",
            "Student Name"
        ]

        for header in required_attendance_headers:

            if header not in attendance_headers:
                result.add_error(
                    f"Missing column '{header}' in Attendance Details sheet."
                )

        return result