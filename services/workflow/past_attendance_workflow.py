from datetime import datetime
from config.config import Config
from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.batch_validator import BatchValidator
from services.attendance.processor import AttendanceProcessor
from services.attendance.updater import AttendanceUpdater
from utils.logger import logger

class PastAttendanceWorkflow:
    """
    Handles adding attendance for a past date
    using morning and afternoon batch files.
    """

    def process(
        self,
        date,
        morning_path,
        afternoon_path,
        urn_overrides=None
    ):

        # -----------------------------
        # Validate Date Format
        # -----------------------------
        date_format = Config.get_date_format()

        try:
            datetime.strptime(date, date_format)
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format."
            }

        # -----------------------------
        # Block Future Dates
        # -----------------------------

        selected = datetime.strptime(date, date_format)
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if selected >= today:
            return {
                "success": False,
                "error": "Only past dates are allowed."
            }

        # -----------------------------
        # Load Workbook
        # -----------------------------

        manager = WorkbookManager()
        workbook_path = manager.get_registered_workbook()

        if workbook_path is None:
            return {
                "success": False,
                "error": "No master workbook is registered. Please upload one first."
            }

        loader = WorkbookLoader(workbook_path)
        loader.load_workbook()
        workbook = loader.get_workbook()
        student_sheet = loader.get_student_sheet()
        attendance_sheet = loader.get_attendance_sheet()

        # -----------------------------
        # Check Date Already Exists
        # -----------------------------

        for col in range(3, attendance_sheet.max_column + 1):

            if attendance_sheet.cell(
                row=1,
                column=col
            ).value == date:

                return {
                    "success": False,
                    "error": f"Attendance for {date} already exists. Use Edit Past Attendance to modify it."
                }

        # -----------------------------
        # Load Master Students
        # -----------------------------

        headers = [
            cell.value
            for cell in student_sheet[1]
        ]

        master_students = []

        for row in student_sheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            if all(cell is None for cell in row):
                continue

            master_students.append(
                dict(zip(headers, row))
            )

        # -----------------------------
        # Validate Batches
        # -----------------------------

        morning_result = BatchValidator(
            morning_path,
            student_sheet
        ).validate(urn_overrides=urn_overrides or {})

        afternoon_result = BatchValidator(
            afternoon_path,
            student_sheet
        ).validate(urn_overrides=urn_overrides or {})

        if not morning_result.is_valid or not afternoon_result.is_valid:

            return {
                "success": False,
                "morning": morning_result,
                "afternoon": afternoon_result,
                "validation_error": True
            }

        # Check for duplicates needing URN clarification
        all_duplicates = (
            morning_result.duplicates +
            afternoon_result.duplicates
        )

        if all_duplicates:
            return {
                "success": False,
                "duplicates_found": True,
                "duplicates": all_duplicates
            }

        unknown_morning = morning_result.warnings
        unknown_afternoon = afternoon_result.warnings

        # -----------------------------
        # Process Attendance
        # -----------------------------

        processor = AttendanceProcessor(
            master_students,
            morning_result.data,
            afternoon_result.data
        )

        attendance_result = processor.process()

        # -----------------------------
        # Update Workbook
        # -----------------------------

        updater = AttendanceUpdater(
            workbook,
            workbook_path,
            student_sheet,
            attendance_sheet,
            attendance_result
        )

        # Override date in updater
        updater._target_date = date

        updater.update()
        updater.save()
        logger.info(
            f"Past attendance processed for {date}: "
            f"{len(attendance_result)} students"
        )
        total = len(attendance_result)
        present = [s for s in attendance_result if s["Status"] == "P"]
        absent = [s for s in attendance_result if s["Status"] == "A"]

        return {
            "success": True,
            "unknown_morning": unknown_morning,
            "unknown_afternoon": unknown_afternoon,
            "summary": {
                "total": total,
                "present": len(present),
                "absent": len(absent),
                "absent_students": [s["Student Name"] for s in absent]
            }
        }