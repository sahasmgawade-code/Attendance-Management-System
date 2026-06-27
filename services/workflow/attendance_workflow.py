from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.batch_validator import BatchValidator
from services.attendance.processor import AttendanceProcessor
from services.attendance.updater import AttendanceUpdater
from datetime import datetime


class AttendanceWorkflow:

    def attendance_exists(self, attendance_sheet):

        today = datetime.now().strftime("%d-%m-%Y")

        for col in range(3, attendance_sheet.max_column + 1):

            if attendance_sheet.cell(
                row=1,
                column=col
            ).value == today:

                return True

        return False

    def process(
        self,
        morning_path,
        afternoon_path,
        overwrite=False
    ):

        manager = WorkbookManager()

        workbook_path = manager.get_registered_workbook()

        loader = WorkbookLoader(workbook_path)
        loader.load_workbook()

        workbook = loader.get_workbook()

        student_sheet = loader.get_student_sheet()

        attendance_sheet = loader.get_attendance_sheet()

        if self.attendance_exists(attendance_sheet) and not overwrite:

            return {
                "success": False,
                "attendance_exists": True
            }

        # -----------------------------
        # Load Master Students
        # -----------------------------

        master_students = self._load_master_students(
            student_sheet
        )

        # -----------------------------
        # Validate Batches
        # -----------------------------

        morning_result = BatchValidator(
            morning_path,
            student_sheet
        ).validate()

        afternoon_result = BatchValidator(
            afternoon_path,
            student_sheet
        ).validate()

        if not morning_result.is_valid or not afternoon_result.is_valid:

            return {
                "success": False,
                "morning": morning_result,
                "afternoon": afternoon_result
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

        updater.update()
        updater.save()

        total = len(attendance_result)
        present = [s for s in attendance_result if s["Status"] == "P"]
        absent = [s for s in attendance_result if s["Status"] == "A"]


        return {
            "success": True,
            "attendance": attendance_result,
            "unknown_morning": unknown_morning,
            "unknown_afternoon": unknown_afternoon,
            "summary": {
                "total": total,
                "present": len(present),
                "absent": len(absent),
                "absent_students": [s["Student Name"] for s in absent]
            }           
        }

    # -----------------------------------

    def _load_master_students(
        self,
        student_sheet
    ):

        headers = [
            cell.value
            for cell in student_sheet[1]
        ]

        students = []

        for row in student_sheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            if all(cell is None for cell in row):
                continue

            students.append(
                dict(zip(headers, row))
            )

        return students