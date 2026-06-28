import re

from models.validation import ValidationResult


class MasterValidator:
    """
    Validates the data present in the
    Student Details worksheet.
    """

    EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    def __init__(self, student_sheet):
        self.student_sheet = student_sheet
        self.students = []

    def validate(self) -> ValidationResult:

        result = ValidationResult()

        self._load_students()

        self._validate_urn(result)
        self._validate_student_name(result)
        self._validate_email(result)
        self._validate_student_phone(result)
        self._validate_parent_phone(result)
        self._validate_present_count(result)
        self._validate_working_days(result)

        self._check_duplicate_names(result)
        self._check_duplicate_parent_numbers(result)

        return result

    # --------------------------------------------------
    # Load Data
    # --------------------------------------------------

    def _load_students(self):

        headers = [
            cell.value
            for cell in self.student_sheet[1]
        ]

        for row_number, row in enumerate(
                self.student_sheet.iter_rows(min_row=2, values_only=True),
                start=2):

            if all(cell is None for cell in row):
                continue

            student = dict(zip(headers, row))
            student["Row"] = row_number

            self.students.append(student)

    # --------------------------------------------------
    # Validation Methods
    # --------------------------------------------------

    def _validate_urn(self, result):

        urns = set()

        for student in self.students:

            urn = student["URN"]

            if urn in (None, ""):
                result.add_error(
                    f"Row {student['Row']}: URN cannot be empty."
                )

            elif urn in urns:
                result.add_error(
                    f"Row {student['Row']}: Duplicate URN '{urn}'."
                )

            else:
                urns.add(urn)

    def _validate_student_name(self, result):

        for student in self.students:

            if student["Student Name"] in (None, ""):
                result.add_error(
                    f"Row {student['Row']}: Student Name cannot be empty."
                )

    def _validate_email(self, result):

        emails = set()

        for student in self.students:

            email = student["Student Email"]

            if email in (None, ""):
                result.add_error(
                    f"Row {student['Row']}: Student Email cannot be empty."
                )
                continue

            if not re.match(self.EMAIL_PATTERN, str(email)):
                result.add_error(
                    f"Row {student['Row']}: Invalid Email '{email}'."
                )
                continue

            if email in emails:
                result.add_error(
                    f"Row {student['Row']}: Duplicate Email '{email}'."
                )
                continue

            emails.add(email)

    def _validate_student_phone(self, result):

        phones = set()

        for student in self.students:

            phone = student["Student Phone"]

            if phone in (None, ""):
                result.add_error(
                    f"Row {student['Row']}: Student Phone cannot be empty."
                )

            elif phone in phones:
                result.add_error(
                    f"Row {student['Row']}: Duplicate Student Phone '{phone}'."
                )

            else:
                phones.add(phone)

    def _validate_parent_phone(self, result):

        for student in self.students:

            if student["Parent Phone"] in (None, ""):
                result.add_error(
                    f"Row {student['Row']}: Parent Phone cannot be empty."
                )

    def _validate_present_count(self, result):

        for student in self.students:

            value = student["Present Count"]

            if value is None or not isinstance(value, (int, float)) or int(value) != value or value < 0:
                result.add_error(
                    f"Row {student['Row']}: Present Count must be a non-negative integer."
                )

    def _validate_working_days(self, result):

        for student in self.students:

            value = student["Working Days"]

            if value is None or not isinstance(value, (int, float)) or int(value) != value or value < 0:
                result.add_error(
                    f"Row {student['Row']}: Working Days must be a non-negative integer."
                )
    # --------------------------------------------------
    # Warning Methods
    # --------------------------------------------------

    def _check_duplicate_names(self, result):

        names = {}

        for student in self.students:

            names.setdefault(
                student["Student Name"],
                []
            ).append(student["Row"])

        for name, rows in names.items():

            if name and len(rows) > 1:

                result.add_warning(
                    f"Duplicate Student Name '{name}' found in rows {rows}."
                )

    def _check_duplicate_parent_numbers(self, result):

        numbers = {}

        for student in self.students:

            numbers.setdefault(
                student["Parent Phone"],
                []
            ).append(student["Row"])

        for phone, rows in numbers.items():

            if phone and len(rows) > 1:

                result.add_warning(
                    f"Duplicate Parent Phone '{phone}' found in rows {rows}."
                )