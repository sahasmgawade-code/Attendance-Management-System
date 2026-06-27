from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader
from services.workbook.validator import WorkbookValidator


def main():

    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    if workbook_path is None:
        print("No workbook registered.")
        return

    loader = WorkbookLoader(workbook_path)
    loader.load_workbook()

    validator = WorkbookValidator(
        loader.get_workbook()
    )

    result = validator.validate_workbook()

    print(f"Workbook Valid : {result.is_valid}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f" - {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f" - {warning}")


if __name__ == "__main__":
    main()