from config.config import Config
from datetime import datetime

class AttendanceUpdater:
    """
    Updates the master workbook with attendance data.

    Responsibilities:
    1. Synchronize Attendance Details with Student Details.
    2. Create today's date column if required.
    3. Write P/A.
    4. Update Present Count, Working Days and Attendance %.
    5. Save workbook.
    """

    def __init__(
        self,
        workbook,
        workbook_path,
        student_sheet,
        attendance_sheet,
        attendance_result
    ):

        self.workbook = workbook
        self.workbook_path = workbook_path

        self.student_sheet = student_sheet
        self.attendance_sheet = attendance_sheet
        self.attendance_result = attendance_result
    # =====================================================
    # PUBLIC
    # =====================================================

    def update(self):

        # Step 1
        self._sync_attendance_sheet()

        # Step 2
        date_column, is_new_day = self._get_or_create_date_column()
        # Step 3
        student_rows = self._create_row_map(self.student_sheet)
        attendance_rows = self._create_row_map(self.attendance_sheet)

        student_headers = [
            cell.value
            for cell in self.student_sheet[1]
        ]

        present_col = student_headers.index("Present Count") + 1
        working_col = student_headers.index("Working Days") + 1
        percentage_col = student_headers.index("Attendance %") + 1

        for student in self.attendance_result:

            urn = student["URN"]
            status = student["Status"]

            # -------------------------
            # Attendance Details
            # -------------------------
            if urn not in attendance_rows or urn not in student_rows:
                continue

            attendance_row = attendance_rows[urn]
            student_row = student_rows[urn]

            # Write today's status first
            self.attendance_sheet.cell(
                row=attendance_row,
                column=date_column
            ).value = status

            # Recalculate working days and present
            # count from scratch across all dates
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

    def save(self):

        try:

            self.workbook.save(self.workbook_path)

        except PermissionError:

            raise PermissionError(
                "The master workbook is currently open.\n"
                "Please close the Excel file and try again."
            )
    # =====================================================
    # PRIVATE
    # =====================================================

    def _sync_attendance_sheet(self):
        """
        Copies missing students from Student Details
        into Attendance Details.
        """

        attendance_rows = self._create_row_map(
            self.attendance_sheet
        )

        next_row = self.attendance_sheet.max_row + 1

        for row in self.student_sheet.iter_rows(
                min_row=2,
                values_only=True):

            if all(cell is None for cell in row):
                continue

            urn = row[0]
            name = row[1]

            if urn in attendance_rows:
                continue

            self.attendance_sheet.cell(
                row=next_row,
                column=1
            ).value = urn

            self.attendance_sheet.cell(
                row=next_row,
                column=2
            ).value = name

            next_row += 1

    def _get_or_create_date_column(self):

        today = getattr(
            self,
            "_target_date",
            datetime.now().strftime(Config.get_date_format())
        )
        for col in range(3, self.attendance_sheet.max_column + 1):

            value = self.attendance_sheet.cell(
                row=1,
                column=col
            ).value

            if value == today:

                return col, False

        new_col = self.attendance_sheet.max_column + 1

        self.attendance_sheet.cell(
            row=1,
            column=new_col
        ).value = today

        return new_col, True
    
    @staticmethod
    def _create_row_map(sheet):

        rows = {}

        for row in range(2, sheet.max_row + 1):

            urn = sheet.cell(
                row=row,
                column=1
            ).value

            if urn is not None:
                rows[urn] = row

        return rows