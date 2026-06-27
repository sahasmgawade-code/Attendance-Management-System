import os
from flask import Blueprint
from flask import render_template

from services.workbook.manager import WorkbookManager


home_bp = Blueprint(
    "home",
    __name__
)


@home_bp.route("/")
def home():

    manager = WorkbookManager()

    workbook = manager.get_registered_workbook()

    if workbook is None:

        return render_template(
            "upload_master.html"
        )

    return render_template(
        "dashboard.html",
        workbook=os.path.basename(workbook),
        errors=[],
        success=None,
        attendance_exists=False,
        unknown_morning=[],
        unknown_afternoon=[],
        summary = None
    )