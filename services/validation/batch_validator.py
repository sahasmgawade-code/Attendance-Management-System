import pandas as pd

from models.validation import ValidationResult


class BatchValidator:
    """
    Validates a Morning/Afternoon batch file against
    the Master Workbook. Matching is done strictly by URN.
    """

    def __init__(self, batch_file_path, student_sheet):
        self.batch_file_path = batch_file_path
        self.student_sheet = student_sheet

        self.master_by_urn = {}

    def validate(self, urn_overrides=None) -> ValidationResult:
        # urn_overrides is accepted for backward compatibility with
        # existing callers, but is no longer used now that matching
        # is strictly URN-based (no ambiguity to resolve).

        result = ValidationResult()

        self._load_master_students()

        try:

            with open(self.batch_file_path, "rb") as f:
                signature = f.read(4)

            # .xlsx/.xlsm files are ZIP archives and start with "PK"
            if signature[:2] == b"PK":
                df = pd.read_excel(self.batch_file_path)
            else:
                df = pd.read_csv(self.batch_file_path)

        except Exception as e:

            result.add_error(f"Unable to read batch file.\n{e}")
            return result

        if df.empty:
            result.add_error("Batch file is empty.")
            return result

        if "URN" not in df.columns:
            result.add_error(
                "Batch file must contain a 'URN' column. "
                "Name-based matching is no longer supported."
            )
            return result

        matched_students = []
        seen_urns = set()

        for value in df["URN"]:

            if pd.isna(value):
                continue

            urn = str(value).strip()

            if not urn:
                continue

            if urn in seen_urns:
                continue

            seen_urns.add(urn)

            student = self.master_by_urn.get(urn)

            if student is None:
                result.add_warning(
                    f"URN '{urn}' not found in Master Data."
                )
                continue

            matched_students.append(student)

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

            urn = str(student.get("URN", "")).strip()

            if urn:
                self.master_by_urn[urn] = student