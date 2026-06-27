from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader


class AttendanceEditor:
    """
    Handles reading and editing attendance
    for a specific past date.
    """

    def __init__(self):

        manager = WorkbookManager()
        workbook_path = manager.get_registered_workbook()

        self.loader = WorkbookLoader(workbook_path)
        self.loader.load_workbook()

        self.workbook = self.loader.get_workbook()
        self.workbook_path = workbook_path
        self.student_sheet = self.loader.get_student_sheet()
        self.attendance_sheet = self.loader.get_attendance_sheet()

    # =====================================================
    # PUBLIC
    # =====================================================

    def get_dates(self):
        """
        Returns all recorded dates from
        the Attendance Details sheet.
        """

        dates = []

        for col in range(3, self.attendance_sheet.max_column + 1):

            value = self.attendance_sheet.cell(
                row=1,
                column=col
            ).value

            if value:
                dates.append(value)

        return dates

    def get_attendance_for_date(self, date):
        """
        Returns all students with their
        P/A status for the given date.
        """

        # Find date column
        date_col = self._get_date_column(date)

        if date_col is None:
            return []

        students = []

        for row in range(2, self.attendance_sheet.max_row + 1):

            urn = self.attendance_sheet.cell(
                row=row,
                column=1
            ).value

            name = self.attendance_sheet.cell(
                row=row,
                column=2
            ).value

            if urn is None:
                continue

            status = self.attendance_sheet.cell(
                row=row,
                column=date_col
            ).value or "A"

            students.append({
                "urn": urn,
                "name": name,
                "status": status
            })

        return students

    def save_edits(self, date, edits):
        """
        Saves edited attendance for a date.
        edits = { urn: "P" or "A" }
        Recalculates all counts from scratch.
        """

        date_col = self._get_date_column(date)

        if date_col is None:
            return False

        # Build row maps
        attendance_rows = self._create_row_map(
            self.attendance_sheet
        )

        student_rows = self._create_row_map(
            self.student_sheet
        )

        student_headers = [
            cell.value
            for cell in self.student_sheet[1]
        ]

        present_col = student_headers.index("Present Count") + 1
        working_col = student_headers.index("Working Days") + 1
        percentage_col = student_headers.index("Attendance %") + 1

        for urn, status in edits.items():

            # Convert urn to match sheet type
            urn = self._match_urn(urn, attendance_rows)

            if urn is None:
                continue

            if urn not in attendance_rows or urn not in student_rows:
                continue

            attendance_row = attendance_rows[urn]
            student_row = student_rows[urn]

            # Write new status
            self.attendance_sheet.cell(
                row=attendance_row,
                column=date_col
            ).value = status

            # Recalculate from scratch
            working = 0
            present = 0

            for col in range(3, self.attendance_sheet.max_column + 1):

                cell_val = self.attendance_sheet.cell(
                    row=attendance_row,
                    column=col
                ).value

                if cell_val in ("P", "A"):
                    working += 1

                if cell_val == "P":
                    present += 1

            percentage = (
                (present / working) * 100
                if working else 0
            )

            self.student_sheet.cell(
                row=student_row,
                column=present_col
            ).value = present

            self.student_sheet.cell(
                row=student_row,
                column=working_col
            ).value = working

            self.student_sheet.cell(
                row=student_row,
                column=percentage_col
            ).value = round(percentage, 2)

        # Save workbook
        try:
            self.workbook.save(self.workbook_path)
            return True

        except PermissionError:
            raise PermissionError(
                "The master workbook is currently open.\n"
                "Please close the Excel file and try again."
            )

    # =====================================================
    # PRIVATE
    # =====================================================

    def _get_date_column(self, date):

        for col in range(3, self.attendance_sheet.max_column + 1):

            if self.attendance_sheet.cell(
                row=1,
                column=col
            ).value == date:

                return col

        return None

    def _create_row_map(self, sheet):

        rows = {}

        for row in range(2, sheet.max_row + 1):

            urn = sheet.cell(
                row=row,
                column=1
            ).value

            if urn is not None:
                rows[urn] = row

        return rows

    def _match_urn(self, urn_str, attendance_rows):
        """
        Matches URN from form (always string)
        to the correct type in the sheet.
        """

        # Try direct match
        if urn_str in attendance_rows:
            return urn_str

        # Try int match (Excel stores URNs as numbers)
        try:
            urn_int = int(urn_str)
            if urn_int in attendance_rows:
                return urn_int
        except ValueError:
            pass

        return None
        