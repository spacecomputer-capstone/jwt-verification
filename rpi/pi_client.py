import socket
import threading
import requests
from rpi_bridge import app
from config import (
    BACKEND_URL,
    PI_ID,
    RPI_BRIDGE_HOST,
    RPI_BRIDGE_PORT,
    RPI_BRIDGE_ADVERTISED_URL,
    HEARTBEAT_INTERVAL_SECONDS,
)


def _bridge_url():
    if RPI_BRIDGE_ADVERTISED_URL:
        return RPI_BRIDGE_ADVERTISED_URL.rstrip("/")
    host = socket.gethostname()
    return f"http://{host}.local:{RPI_BRIDGE_PORT}"


def _heartbeat_loop(stop_evt: threading.Event):
    payload = {
        "pi_id": PI_ID,
        "bridge_url": _bridge_url(),
        "status": "online",
    }
    while not stop_evt.wait(HEARTBEAT_INTERVAL_SECONDS):
        try:
            requests.post(
                f"{BACKEND_URL}/presence/pi/heartbeat",
                json=payload,
                timeout=3,
            )
        except Exception:
            # Keep bridge serving even if backend is temporarily unreachable.
            pass

if __name__ == "__main__":
    stop_evt = threading.Event()
    threading.Thread(target=_heartbeat_loop, args=(stop_evt,), daemon=True).start()

    print(f"Starting Pi bridge for {PI_ID} on http://{RPI_BRIDGE_HOST}:{RPI_BRIDGE_PORT}")
    print(f"Heartbeat -> {BACKEND_URL}/presence/pi/heartbeat every {HEARTBEAT_INTERVAL_SECONDS}s")
    print(f"Advertised bridge URL: {_bridge_url()}")
    print("Endpoints: GET /health, GET /challenge")
    try:
        app.run(host=RPI_BRIDGE_HOST, port=RPI_BRIDGE_PORT, debug=False)
    finally:
        stop_evt.set()
