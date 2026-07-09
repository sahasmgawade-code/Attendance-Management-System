from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.batch_validator import BatchValidator


def main():

    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    loader = WorkbookLoader(workbook_path)

    loader.load_workbook()

    validator = BatchValidator(

        batch_file_path="Attendance Report - SLOT1 (22-Jun-2026).csv",

        student_sheet=loader.get_student_sheet()

    )

    result = validator.validate()

    print(f"Batch Valid : {result.is_valid}")

    if result.errors:

        print("\nERRORS")

        for error in result.errors:
            print(error)

    if result.warnings:

        print("\nWARNINGS")

        for warning in result.warnings:
            print(warning)

    if result.data:

        print("\nMatched Students")

        for student in result.data:

            print("-" * 40)

            for key, value in student.items():
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()

def test_batch_validator_runs():
    """Smoke test: ensures the batch validator script runs without raising."""
    main()