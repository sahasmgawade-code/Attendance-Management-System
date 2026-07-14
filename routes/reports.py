from datetime import datetime
from flask import Blueprint
from flask import render_template
from flask import request
from flask import send_file
from utils.auth import login_required
from services.reporting.report_service import ReportService
from services.reporting.pdf_service import PDFReportService
from services.workbook.manager import WorkbookManager
from datetime import datetime
from config.config import Config
from services.attendance.editor import AttendanceEditor

reports_bp = Blueprint(
    "reports",
    __name__
)


@reports_bp.route("/reports")
@login_required
def reports():

    manager = WorkbookManager()

    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    service = ReportService()

    students = service.get_all_students()

    # Selected student from dropdown
    selected_urn = request.args.get("urn")

    selected_student = None
    absent_dates = []

    if selected_urn:

        for s in students:
            if str(s["urn"]) == str(selected_urn):
                selected_student = s
                break

        if selected_student:
            absent_dates = service.get_absent_dates(selected_urn)

    # Defaulters — below 75%
    defaulters = [s for s in students if s["defaulter"]]

    return render_template(
        "reports.html",
        students=students,
        selected_student=selected_student,
        selected_urn=selected_urn,
        absent_dates=absent_dates,
        defaulters=defaulters
    )

@reports_bp.route("/reports/download")
@login_required
def download_report():

    manager = WorkbookManager()

    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    service = ReportService()
    students = service.get_all_students()

    pdf_service = PDFReportService()
    buffer = pdf_service.generate(students)

    filename = f"Attendance_Report_{datetime.now().strftime('%d-%m-%Y')}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

@reports_bp.route("/reports/today")
@login_required
def today_attendance():

    manager = WorkbookManager()
    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    today_str = datetime.now().strftime(Config.get_date_format())

    editor = AttendanceEditor()
    students = editor.get_attendance_for_date(today_str)

    present_count = sum(1 for s in students if s["status"] == "P")
    absent_count = sum(1 for s in students if s["status"] == "A")

    return render_template(
        "today_attendance.html",
        today=today_str,
        students=students,
        present_count=present_count,
        absent_count=absent_count
    )