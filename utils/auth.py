import os
import json
from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.security import check_password_hash


def _load_users():
    """
    Reads ADMIN_USERS from environment as JSON, e.g.:
    {"sahas":"scrypt:...", "priya":"scrypt:...", "office":"scrypt:..."}
    """
    raw = os.environ.get("ADMIN_USERS", "{}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def verify_credentials(username, password):
    users = _load_users()
    stored_hash = users.get(username)
    if not stored_hash:
        return False
    return check_password_hash(stored_hash, password)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped