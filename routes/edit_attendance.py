from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from services.attendance.editor import AttendanceEditor
from services.workbook.manager import WorkbookManager


edit_bp = Blueprint(
    "edit",
    __name__
)


@edit_bp.route("/attendance/edit", methods=["GET"])
def edit_attendance():

    manager = WorkbookManager()

    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    editor = AttendanceEditor()

    dates = editor.get_dates()

    selected_date = request.args.get("date")

    students = []

    if selected_date:
        students = editor.get_attendance_for_date(selected_date)

    return render_template(
        "edit_attendance.html",
        dates=dates,
        selected_date=selected_date,
        students=students
    )


@edit_bp.route("/attendance/edit", methods=["POST"])
def save_attendance():

    selected_date = request.form.get("date")

    # Build edits dict from form
    edits = {}

    for key, value in request.form.items():

        if key.startswith("status_"):
            urn = key.replace("status_", "")
            edits[urn] = value

    try:

        editor = AttendanceEditor()
        editor.save_edits(selected_date, edits)

        return redirect(
            url_for(
                "edit.edit_attendance",
                date=selected_date,
                success="true"
            )
        )

    except PermissionError as e:

        editor = AttendanceEditor()
        dates = editor.get_dates()
        students = editor.get_attendance_for_date(selected_date)

        return render_template(
            "edit_attendance.html",
            dates=dates,
            selected_date=selected_date,
            students=students,
            error=str(e)
        )