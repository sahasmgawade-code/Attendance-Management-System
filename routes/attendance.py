import os

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
        "morning.csv"
    )

    afternoon_path = os.path.join(
        BATCH_FOLDER,
        "afternoon.csv"
    )

    overwrite = request.form.get("overwrite") == "true"

    # ------------------------------------------
    # First Request
    # Save Uploaded Files
    # ------------------------------------------

    if not overwrite:

        morning_file = request.files["morning_batch"]
        afternoon_file = request.files["afternoon_batch"]

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
                summary=None                
            )
    # ------------------------------------------
    # Execute Workflow
    # ------------------------------------------
    manager = WorkbookManager()

    workbook_path = manager.get_registered_workbook()

    workbook_name = os.path.basename(workbook_path)

    workflow = AttendanceWorkflow()
    
    try:

        result = workflow.process(
            morning_path,
            afternoon_path,
            overwrite=overwrite
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
            summary=None
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
                errors=[ ],
                attendance_exists = True,
                unknown_morning=[],
                unknown_afternoon=[],
                summary = None
            )

        # --------------------------------------
        # Batch Validation Errors
        # --------------------------------------

        errors = []

        errors.extend(
            result["morning"].errors
        )

        errors.extend(
            result["afternoon"].errors
        )

        return render_template(
            "dashboard.html",
            workbook=workbook_name,
            success=None,
            errors=errors,
            attendance_exists=False,
            unknown_morning=[],
            unknown_afternoon=[],
            summary = None
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
        summary = result.get("summary")
    )