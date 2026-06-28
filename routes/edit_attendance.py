from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
from services.attendance.editor import AttendanceEditor
from services.workbook.manager import WorkbookManager

edit_bp = Blueprint("edit", __name__)


def to_picker(date_str):
    """Convert dd-mm-yyyy to yyyy-mm-dd for the HTML date input."""
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def from_picker(date_str):
    """Convert yyyy-mm-dd to dd-mm-yyyy to match workbook dates."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return ""


@edit_bp.route("/attendance/edit", methods=["GET"])
def edit_attendance():

    manager = WorkbookManager()
    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    editor = AttendanceEditor()
    dates = editor.get_dates()

    picker_dates = [to_picker(d) for d in dates]
    min_date = min(picker_dates) if picker_dates else ""
    max_date = max(picker_dates) if picker_dates else ""

    raw = request.args.get("date", "")
    if raw and len(raw) == 10 and raw[4] == "-":
        selected_date = from_picker(raw)   # yyyy-mm-dd from picker
        picker_value = raw
    else:
        selected_date = raw                # dd-mm-yyyy from redirect
        picker_value = to_picker(raw)

    students = []
    error = None

    if selected_date:
        if selected_date not in dates:
            error = f"No attendance recorded for {selected_date}."
        else:
            students = editor.get_attendance_for_date(selected_date)

    return render_template(
        "edit_attendance.html",
        dates=dates,
        selected_date=selected_date,
        picker_value=picker_value,
        min_date=min_date,
        max_date=max_date,
        students=students,
        error=error
    )


@edit_bp.route("/attendance/edit", methods=["POST"])
def save_attendance():

    selected_date = request.form.get("date")
    edits = {}

    for key, value in request.form.items():
        if key.startswith("status_"):
            edits[key.replace("status_", "")] = value

    try:
        editor = AttendanceEditor()
        editor.save_edits(selected_date, edits)
        return redirect(url_for("edit.edit_attendance", date=selected_date, success="true"))

    except PermissionError as e:
        editor = AttendanceEditor()
        dates = editor.get_dates()
        picker_dates = [to_picker(d) for d in dates]
        min_date = min(picker_dates) if picker_dates else ""
        max_date = max(picker_dates) if picker_dates else ""

        return render_template(
            "edit_attendance.html",
            dates=dates,
            selected_date=selected_date,
            picker_value=to_picker(selected_date),
            min_date=min_date,
            max_date=max_date,
            students=editor.get_attendance_for_date(selected_date),
            error=str(e)
        )