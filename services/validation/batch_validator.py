import pandas as pd

from models.validation import ValidationResult


class BatchValidator:
    """
    Validates a Morning/Afternoon batch file against
    the Master Workbook.
    """

    REQUIRED_COLUMN = "Participant Name"

    def __init__(self, batch_file_path, student_sheet):
        self.batch_file_path = batch_file_path
        self.student_sheet = student_sheet

        self.master_students = {}
        self.batch_students = set()

    def validate(self) -> ValidationResult:

        result = ValidationResult()

        self._load_master_students()

        try:

            if self.batch_file_path.lower().endswith(".csv"):
                df = pd.read_csv(self.batch_file_path)

            else:
                df = pd.read_excel(self.batch_file_path)

        except Exception as e:

            result.add_error(f"Unable to read batch file.\n{e}")
            return result

        if df.empty:
            result.add_error("Batch file is empty.")
            return result

        if self.REQUIRED_COLUMN not in df.columns:
            result.add_error(
                f"Required column '{self.REQUIRED_COLUMN}' not found."
            )
            return result

        matched_students = []

        for name in df[self.REQUIRED_COLUMN]:

            if pd.isna(name):
                continue

            normalized = self._normalize_name(name)

            # Ignore duplicate joins
            if normalized in self.batch_students:
                continue

            self.batch_students.add(normalized)

            # Student not found — check if all words are a subset of any master name
            matched_key = None

            for master_key in self.master_students:
                if normalized <= master_key:
                    matched_key = master_key
                    break

            if matched_key is None:

                result.add_warning(
                    f"Student '{name}' not found in Master Data."
                )
                continue

            matches = self.master_students[matched_key]

            # Duplicate student names in master
            if len(matches) > 1:

                result.add_error(
                    f"Multiple students found with name '{name}'."
                )
                continue

            matched_students.append(matches[0])

        result.data = matched_students

        return result

    # ---------------------------------------------------------

    def _load_master_students(self):

        headers = [
            cell.value
            for cell in self.student_sheet[1]
        ]

        for row in self.student_sheet.iter_rows(
                min_row=2,
                values_only=True):

            if all(cell is None for cell in row):
                continue

            student = dict(zip(headers, row))

            normalized = self._normalize_name(
                student["Student Name"]
            )

            self.master_students.setdefault(
                normalized,
                []
            ).append(student)

    # ---------------------------------------------------------

    @staticmethod
    def _normalize_name(name):
        words = str(name).strip().lower().split()
        return frozenset(words)