from io import BytesIO

from openpyxl import Workbook


def generate_excel_bytes(session):

    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"

    ws.append([
        "URN",
        "Full Name",
        "Submitted At",
        "Device IP"
    ])

    for response in session["responses"]:
        full_name = " ".join([
            response["first_name"],
            response["middle_name"],
            response["last_name"]
        ])

        ws.append([
            response["urn"],
            full_name,
            response["submitted_at"].strftime("%d-%m-%Y %H:%M:%S"),
            response["device_ip"]
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return buffer