import os
from datetime import datetime
from flask import Blueprint
from flask import request
from flask import render_template

from services.workbook.manager import WorkbookManager
from services.workflow.attendance_workflow import AttendanceWorkflow


attendance_bp = Blueprint(
    "attendance",
    __name__
)

BATCH_FOLDER = "uploads/batches"


@attendance_bp.route(
    "/attendance/process",
    methods=["POST"]
)
def process_attendance():

    # ------------------------------------------
    # Save Uploaded Files
    # ------------------------------------------

    os.makedirs(BATCH_FOLDER, exist_ok=True)

    morning_path = os.path.join(
        BATCH_FOLDER,
        "morning.batch"
    )

    afternoon_path = os.path.join(
        BATCH_FOLDER,
        "afternoon.batch"
    )

    overwrite = request.form.get("overwrite") == "true"
    # Collect URN overrides for duplicate names
    urn_overrides = {}
    for key, value in request.form.items():
        if key.startswith("urn_override_"):
            name = key.replace("urn_override_", "").replace("_", " ")
            urn_overrides[name.lower()] = value.strip()    

    # ------------------------------------------
    # First Request
    # Save Uploaded Files
    # ------------------------------------------

    if not overwrite:

        morning_file = request.files.get("morning_batch")
        afternoon_file = request.files.get("afternoon_batch")

        if not morning_file or not afternoon_file or morning_file.filename == "" or afternoon_file.filename == "":

            manager = WorkbookManager()
            workbook_path = manager.get_registered_workbook()
            workbook_name = os.path.basename(workbook_path) if workbook_path else "Unknown"

            return render_template(
                "dashboard.html",
                workbook=workbook_name,
                success=None,
                attendance_exists=False,
                errors=["Please select both the Morning and Afternoon batch files."],
                unknown_morning=[],
                unknown_afternoon=[],
                summary=None,
                duplicates=[],
                today=datetime.now().strftime("%A, %d %B %Y")
            )

        morning_file.save(morning_path)
        afternoon_file.save(afternoon_path)
    # ------------------------------------------
    # Overwrite Request
    # Reuse Existing Files
    # ------------------------------------------

    else:

        if not os.path.exists(morning_path) or not os.path.exists(afternoon_path):

            manager = WorkbookManager()

            workbook_path = manager.get_registered_workbook()

            workbook_name = os.path.basename(workbook_path) if workbook_path else "Unknown"

            return render_template(
                "dashboard.html",
                workbook=workbook_name,
                success=None,
                attendance_exists=False,
                errors=[
                    "Previous batch files were not found. Please upload the files again."
                ],
                unknown_morning=[],
                unknown_afternoon=[],
                summary=None,
                today=datetime.now().strftime("%A, %d %B %Y")                
            )
    # ------------------------------------------
    # Execute Workflow
    # ------------------------------------------
    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    if workbook_path is None:
        return render_template(
            "dashboard.html",
            workbook="Unknown",
            success=None,
            attendance_exists=False,
            errors=["No master workbook is registered. Please upload one first."],
            unknown_morning=[],
            unknown_afternoon=[],
            summary=None,
            duplicates=[],
            today=datetime.now().strftime("%A, %d %B %Y")
        )

    workbook_name = os.path.basename(workbook_path)

    workflow = AttendanceWorkflow()    
    try:

        result = workflow.process(
            morning_path,
            afternoon_path,
            overwrite=overwrite,
            urn_overrides=urn_overrides
        )

    except PermissionError as e:

        return render_template(
            "dashboard.html",
            workbook=workbook_name,
            success=None,
            attendance_exists=False,
            errors=[str(e)],
            unknown_morning=[],
            unknown_afternoon=[],
            summary=None,
            duplicates=[],
            today=datetime.now().strftime("%A, %d %B %Y")
        )
    if result.get("no_workbook"):
        return render_template(
            "dashboard.html",
            workbook="Unknown",
            success=None,
            attendance_exists=False,
            errors=["No master workbook is registered. Please upload one first."],
            unknown_morning=[],
            unknown_afternoon=[],
            summary=None,
            duplicates=[],
            today=datetime.now().strftime("%A, %d %B %Y")
        )

    # ------------------------------------------
    # Validation Failed
    # ------------------------------------------

    if not result["success"]:

        # --------------------------------------
        # Attendance Already Exists
        # --------------------------------------

        if result.get("attendance_exists"):

            return render_template(
                "dashboard.html",
                workbook=workbook_name,
                success=None,
                errors=[],
                attendance_exists=True,
                unknown_morning=[],
                unknown_afternoon=[],
                summary=None,
                duplicates=[],
                today=datetime.now().strftime("%A, %d %B %Y")
            )

        # --------------------------------------
        # Duplicate Names Found
        # --------------------------------------

        if result.get("duplicates_found"):

            return render_template(
                "dashboard.html",
                workbook=workbook_name,
                success=None,
                errors=[],
                attendance_exists=False,
                unknown_morning=[],
                unknown_afternoon=[],
                summary=None,
                duplicates=result.get("duplicates", []),
                today=datetime.now().strftime("%A, %d %B %Y")
            )

        # --------------------------------------
        # Batch Validation Errors
        # --------------------------------------

        errors = []
        errors.extend(result["morning"].errors)
        errors.extend(result["afternoon"].errors)

        return render_template(
            "dashboard.html",
            workbook=workbook_name,
            success=None,
            errors=errors,
            attendance_exists=False,
            unknown_morning=[],
            unknown_afternoon=[],
            summary=None,
            duplicates=[],
            today=datetime.now().strftime("%A, %d %B %Y")
        )
    # ------------------------------------------
    # Success
    # ------------------------------------------

    return render_template(
        "dashboard.html",
        workbook=workbook_name,
        success="Attendance processed successfully.",
        errors=[],
        attendance_exists=False,
        unknown_morning=result.get("unknown_morning", []),
        unknown_afternoon=result.get("unknown_afternoon", []),
        summary=result.get("summary"),
        duplicates=[],
        today=datetime.now().strftime("%A, %d %B %Y")
    )