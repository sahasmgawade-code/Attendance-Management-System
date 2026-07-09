import threading
import uuid
from datetime import datetime, timedelta

SESSION_DURATION_MINUTES = 5
MAX_ENTRIES_PER_DEVICE = 2

_lock = threading.Lock()
_sessions = {}


def create_session():
    token = uuid.uuid4().hex

    with _lock:
        _sessions[token] = {
            "token": token,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=SESSION_DURATION_MINUTES),
            "responses": [],
            "device_counts": {}
        }

    return _sessions[token]


def get_session(token):
    with _lock:
        return _sessions.get(token)


def is_expired(session):
    return datetime.now() >= session["expires_at"]


def device_can_submit(session, device_id):
    with _lock:
        count = session["device_counts"].get(device_id, 0)
        return count < MAX_ENTRIES_PER_DEVICE


def record_submission(session, device_id, response):
    with _lock:
        session["responses"].append(response)
        session["device_counts"][device_id] = session["device_counts"].get(device_id, 0) + 1