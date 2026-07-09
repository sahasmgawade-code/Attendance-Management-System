from services.workbook.manager import WorkbookManager
from services.workbook.loader import WorkbookLoader


def get_valid_urns():
    """
    Returns a set of all URNs currently in the master workbook,
    or None if no workbook is registered.
    """

    manager = WorkbookManager()
    workbook_path = manager.get_registered_workbook()

    if workbook_path is None:
        return None

    loader = WorkbookLoader(workbook_path)
    loader.load_workbook()

    student_sheet = loader.get_student_sheet()

    headers = [cell.value for cell in student_sheet[1]]

    if "URN" not in headers:
        return None

    urn_index = headers.index("URN")

    urns = set()

    for row in student_sheet.iter_rows(min_row=2, values_only=True):
        value = row[urn_index]
        if value is not None:
            urns.add(str(value).strip())

    return urns