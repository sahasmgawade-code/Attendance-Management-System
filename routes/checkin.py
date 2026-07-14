import base64
import uuid
from io import BytesIO
from services.checkin.urn_lookup import get_valid_urns
from flask import Blueprint, render_template, request, send_file, make_response
from utils.auth import login_required
import qrcode

from config.config import Config
from services.checkin.session_manager import (
    create_session,
    get_session,
    is_expired,
    device_can_submit,
    record_submission,
    SESSION_DURATION_MINUTES,
    MAX_ENTRIES_PER_DEVICE
)
from services.checkin.network_check import get_client_ip
from services.checkin.excel_export import generate_excel_bytes
from datetime import datetime


checkin_bp = Blueprint("checkin", __name__)

DEVICE_COOKIE_NAME = "checkin_device_id"


def _wifi_name():
    settings = Config.load_settings()
    return settings.get("checkin_wifi_name", "ADYPU")


@checkin_bp.route("/checkin/generate", methods=["GET"])
@login_required
def generate():

    session = create_session()

    settings = Config.load_settings()
    base_url = settings.get("checkin_base_url", "").rstrip("/")

    checkin_url = f"{base_url}/checkin/{session['token']}"

    qr_img = qrcode.make(checkin_url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    expires_at_ms = int(session["expires_at"].timestamp() * 1000)

    return render_template(
        "checkin_generate.html",
        token=session["token"],
        checkin_url=checkin_url,
        qr_base64=qr_base64,
        expires_at_ms=expires_at_ms,
        duration_minutes=SESSION_DURATION_MINUTES,
        base_url_configured=bool(base_url)
    )


@checkin_bp.route("/checkin/<token>", methods=["GET"])
def checkin_form(token):

    session = get_session(token)

    if session is None:
        return render_template("checkin_form.html", error="invalid", token=token)

    if is_expired(session):
        return render_template("checkin_form.html", error="expired", token=token)

    client_ip = get_client_ip(request)

    resp = make_response(render_template("checkin_form.html", error=None, token=token))

    if not request.cookies.get(DEVICE_COOKIE_NAME):
        resp.set_cookie(DEVICE_COOKIE_NAME, uuid.uuid4().hex, max_age=60 * 60 * 24)

    return resp


@checkin_bp.route("/checkin/<token>", methods=["POST"])
def checkin_submit(token):

    session = get_session(token)

    if session is None:
        return render_template("checkin_form.html", error="invalid", token=token)

    if is_expired(session):
        return render_template("checkin_form.html", error="expired", token=token)

    client_ip = get_client_ip(request)

    device_id = request.cookies.get(DEVICE_COOKIE_NAME)

    if not device_id:
        device_id = uuid.uuid4().hex

    if not device_can_submit(session, device_id):
        resp = make_response(render_template(
            "checkin_form.html",
            error="device_limit",
            token=token
        ))
        resp.set_cookie(DEVICE_COOKIE_NAME, device_id, max_age=60 * 60 * 24)
        return resp

    urn = request.form.get("urn", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not urn or not first_name or not last_name:
        resp = make_response(render_template(
            "checkin_form.html",
            error="missing_fields",
            token=token
        ))
        resp.set_cookie(DEVICE_COOKIE_NAME, device_id, max_age=60 * 60 * 24)
        return resp

    valid_urns = get_valid_urns()

    if valid_urns is None:
        resp = make_response(render_template(
            "checkin_form.html",
            error="no_master_workbook",
            token=token
        ))
        resp.set_cookie(DEVICE_COOKIE_NAME, device_id, max_age=60 * 60 * 24)
        return resp

    if urn not in valid_urns:
        resp = make_response(render_template(
            "checkin_form.html",
            error="invalid_urn",
            submitted_urn=urn,
            token=token
        ))
        resp.set_cookie(DEVICE_COOKIE_NAME, device_id, max_age=60 * 60 * 24)
        return resp
    record_submission(session, device_id, {
        "urn": urn,
        "first_name": first_name,
        "last_name": last_name,
        "submitted_at": datetime.now(),
        "device_ip": client_ip
    })

    resp = make_response(render_template("checkin_form.html", error=None, success=True, token=token))
    resp.set_cookie(DEVICE_COOKIE_NAME, device_id, max_age=60 * 60 * 24)

    return resp


@checkin_bp.route("/checkin/<token>/download", methods=["GET"])
@login_required
def download(token):

    session = get_session(token)

    if session is None:
        return "No such check-in session.", 404

    buffer = generate_excel_bytes(session)

    filename = f"Checkin_Responses_{token[:8]}.xlsx"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@checkin_bp.route("/checkin/<token>/status", methods=["GET"])
@login_required
def status(token):

    session = get_session(token)

    if session is None:
        return {"error": "not_found"}, 404

    return {
        "count": len(session["responses"]),
        "expired": is_expired(session)
    }