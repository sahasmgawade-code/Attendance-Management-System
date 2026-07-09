from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.batch_validator import BatchValidator
from services.attendance.processor import AttendanceProcessor


def load_master_students(student_sheet):

    headers = [cell.value for cell in student_sheet[1]]

    students = []

    for row in student_sheet.iter_rows(min_row=2, values_only=True):

        if all(cell is None for cell in row):
            continue

        students.append(dict(zip(headers, row)))

    return students


def main():

    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    loader = WorkbookLoader(workbook_path)
    loader.load_workbook()

    student_sheet = loader.get_student_sheet()

    master_students = load_master_students(student_sheet)

    morning_validator = BatchValidator(
        "Attendance Report - SLOT1 (22-Jun-2026).csv",
        student_sheet
    )

    afternoon_validator = BatchValidator(
        "Attendance Report - SLOT2 (22-Jun-2026).csv",
        student_sheet
    )

    morning_result = morning_validator.validate()
    afternoon_result = afternoon_validator.validate()

    processor = AttendanceProcessor(
        master_students,
        morning_result.data,
        afternoon_result.data
    )

    attendance = processor.process()

    print()

    for student in attendance:

        print(
            f"{student['URN']} | "
            f"{student['Student Name']} | "
            f"{student['Status']}"
        )


if __name__ == "__main__":
    main()

def test_attendance_processor_runs():
    """Smoke test: ensures the processor script runs without raising."""
    main()