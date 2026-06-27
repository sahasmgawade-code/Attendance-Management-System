from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.batch_validator import BatchValidator
from services.attendance.processor import AttendanceProcessor
from services.attendance.updater import AttendanceUpdater


def load_master_students(student_sheet):

    headers = [cell.value for cell in student_sheet[1]]

    students = []

    for row in student_sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

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
    attendance_sheet = loader.get_attendance_sheet()

    master_students = load_master_students(
        student_sheet
    )

    morning = BatchValidator(
        "Attendance Report - SLOT1 (22-Jun-2026).csv",
        student_sheet
    ).validate()

    afternoon = BatchValidator(
        "Attendance Report - SLOT2 (22-Jun-2026).csv",
        student_sheet
    ).validate()

    processor = AttendanceProcessor(
        master_students,
        morning.data,
        afternoon.data
    )

    attendance_result = processor.process()

    updater = AttendanceUpdater(
        loader.get_workbook(),
        workbook_path,
        student_sheet,
        attendance_sheet,
        attendance_result
    )

    updater.update()
    updater.save()

    print("Attendance updated successfully.")


if __name__ == "__main__":
    main()