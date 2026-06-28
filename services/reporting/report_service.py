from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader


class ReportService:
    """
    Reads the master workbook and provides
    data for the reports page.
    """

    def __init__(self):
        manager = WorkbookManager()
        workbook_path = manager.get_registered_workbook()

        loader = WorkbookLoader(workbook_path)
        loader.load_workbook()

        self.student_sheet = loader.get_student_sheet()

    def get_all_students(self):
        """
        Returns a list of all students with their
        attendance data from the Student Details sheet.
        """

        headers = [
            cell.value
            for cell in self.student_sheet[1]
        ]

        students = []

        for row in self.student_sheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            if all(cell is None for cell in row):
                continue

            student = dict(zip(headers, row))

            present = student.get("Present Count") or 0
            working = student.get("Working Days") or 0

            attendance = (
                round((present / working) * 100, 2)
                if working else 0
            )

            students.append({
                "urn": student["URN"],
                "name": student["Student Name"],
                "present": int(present),
                "working": int(working),
                "attendance": attendance,
                "defaulter": attendance < 75
            })

        return students

    def get_absent_dates(self, urn):
        """
        Returns a list of dates where the student
        was marked Absent.
        """

        loader = WorkbookLoader(
            WorkbookManager().get_registered_workbook()
        )
        loader.load_workbook()
        sheet = loader.get_attendance_sheet()
        headers = [
            sheet.cell(row=1, column=col).value
            for col in range(1, sheet.max_column + 1)
        ]

        for row in range(2, sheet.max_row + 1):

            row_urn = sheet.cell(row=row, column=1).value

            if str(row_urn) != str(urn):
                continue

            absent_dates = []

            for col in range(3, sheet.max_column + 1):

                status = sheet.cell(
                    row=row,
                    column=col
                ).value

                if status == "A":
                    absent_dates.append(headers[col - 1])

            return absent_dates

        return []