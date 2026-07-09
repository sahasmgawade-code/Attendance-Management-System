from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.validation.master_validator import MasterValidator


def main():

    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    loader = WorkbookLoader(workbook_path)
    loader.load_workbook()

    validator = MasterValidator(
        loader.get_student_sheet()
    )

    result = validator.validate()

    print(f"Master Data Valid : {result.is_valid}")

    if result.errors:

        print("\nERRORS")

        for error in result.errors:
            print(error)

    if result.warnings:

        print("\nWARNINGS")

        for warning in result.warnings:
            print(warning)


if __name__ == "__main__":
    main()

def test_master_validator_runs():
    """Smoke test: ensures the master validator script runs without raising."""
    main()    