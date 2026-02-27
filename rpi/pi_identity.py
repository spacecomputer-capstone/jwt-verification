import hashlib
import os
import socket
import uuid
from config import PI_ID as PI_ID_OVERRIDE

BASE_DIR = os.path.dirname(__file__)
PI_ID_PATH = os.path.join(BASE_DIR, ".pi_id")


def _machine_fingerprint() -> str:
    for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    value = f.read().strip()
                    if value:
                        return value
            except Exception:
                pass
    return f"{socket.gethostname()}-{uuid.getnode()}"


def _generate_pi_id() -> str:
    digest = hashlib.sha256(_machine_fingerprint().encode()).hexdigest()[:10]
    return f"pi-{digest}"


def get_pi_id() -> str:
    if PI_ID_OVERRIDE and PI_ID_OVERRIDE.strip():
        return PI_ID_OVERRIDE.strip()

    if os.path.exists(PI_ID_PATH):
        with open(PI_ID_PATH, "r", encoding="utf-8") as f:
            value = f.read().strip()
            if value:
                return value

    pi_id = _generate_pi_id()
    with open(PI_ID_PATH, "w", encoding="utf-8") as f:
        f.write(pi_id + "\n")
    return pi_id
