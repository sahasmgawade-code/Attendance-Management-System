import os
from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from services.workflow.past_attendance_workflow import PastAttendanceWorkflow
from services.workbook.manager import WorkbookManager


past_bp = Blueprint(
    "past",
    __name__
)

BATCH_FOLDER = "uploads/batches/past"


@past_bp.route("/attendance/past", methods=["GET"])
def past_attendance():

    manager = WorkbookManager()

    if manager.get_registered_workbook() is None:
        return render_template("upload_master.html")

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template(
        "past_attendance.html",
        success=None,
        error=None,
        summary=None,
        unknown_morning=[],
        unknown_afternoon=[],
        today = today
    )


@past_bp.route("/attendance/past", methods=["POST"])
def process_past_attendance():

    date = request.form.get("date")

    # Convert date from HTML input (yyyy-mm-dd)
    # to our format (dd-mm-yyyy)
    try:
        parsed = datetime.strptime(date, "%Y-%m-%d")
        date = parsed.strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return render_template(
            "past_attendance.html",
            error="Invalid date selected.",
            success=None,
            summary=None,
            unknown_morning=[],
            unknown_afternoon=[],
            today=datetime.now().strftime("%Y-%m-%d")            
        )

    # Save uploaded files
    os.makedirs(BATCH_FOLDER, exist_ok=True)

    morning_path = os.path.join(BATCH_FOLDER, "morning.csv")
    afternoon_path = os.path.join(BATCH_FOLDER, "afternoon.csv")

    morning_file = request.files.get("morning_batch")
    afternoon_file = request.files.get("afternoon_batch")

    if not morning_file or not afternoon_file:
        return render_template(
            "past_attendance.html",
            error="Please upload both batch files.",
            success=None,
            summary=None,
            unknown_morning=[],
            unknown_afternoon=[],
            today=datetime.now().strftime("%Y-%m-%d")            
        )

    morning_file.save(morning_path)
    afternoon_file.save(afternoon_path)

    # Run workflow
    workflow = PastAttendanceWorkflow()

    try:
        result = workflow.process(
            date,
            morning_path,
            afternoon_path
        )

    except PermissionError as e:
        return render_template(
            "past_attendance.html",
            error=str(e),
            success=None,
            summary=None,
            unknown_morning=[],
            unknown_afternoon=[],
            today=datetime.now().strftime("%Y-%m-%d")            
        )

    # Date already exists error
    if not result["success"] and result.get("error"):
        return render_template(
            "past_attendance.html",
            error=result["error"],
            success=None,
            summary=None,
            unknown_morning=[],
            unknown_afternoon=[],
            today=datetime.now().strftime("%Y-%m-%d")            
        )

    # Validation errors
    if not result["success"] and result.get("validation_error"):

        errors = []
        errors.extend(result["morning"].errors)
        errors.extend(result["afternoon"].errors)

        return render_template(
            "past_attendance.html",
            error=" | ".join(errors),
            success=None,
            summary=None,
            unknown_morning=[],
            unknown_afternoon=[],
            today=datetime.now().strftime("%Y-%m-%d")
        )

    # Success
    return render_template(
        "past_attendance.html",
        success=f"Attendance for {date} added successfully!",
        error=None,
        summary=result.get("summary"),
        unknown_morning=result.get("unknown_morning", []),
        unknown_afternoon=result.get("unknown_afternoon", []),
            today=datetime.now().strftime("%Y-%m-%d")
    )