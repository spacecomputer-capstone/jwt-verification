import socket
import threading
import os
import requests
from rpi_bridge import app
from pi_identity import get_pi_id
from config import (
    BACKEND_URL,
    RPI_BRIDGE_HOST,
    RPI_BRIDGE_PORT,
    RPI_BRIDGE_ADVERTISED_URL,
    HEARTBEAT_INTERVAL_SECONDS,
    PI_REGISTRATION_TOKEN,
)

PI_ID = get_pi_id()
BASE_DIR = os.path.dirname(__file__)

def _bridge_url():
    if RPI_BRIDGE_ADVERTISED_URL:
        return RPI_BRIDGE_ADVERTISED_URL.rstrip("/")
    return f"http://{_lan_ip()}:{RPI_BRIDGE_PORT}"


def _lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def _heartbeat_loop(stop_evt: threading.Event):
    payload = {
        "pi_id": PI_ID,
        "bridge_url": _bridge_url(),
        "status": "online",
    }
    try:
        requests.post(
            f"{BACKEND_URL}/presence/pi/heartbeat",
            json=payload,
            timeout=3,
        )
    except Exception:
        pass

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


def _register_public_key():
    pub_path = os.path.join(BASE_DIR, "keys", "pi_public.pem")
    if not os.path.exists(pub_path):
        print(f"Skipping registration: missing {pub_path}")
        return

    with open(pub_path, "r", encoding="utf-8") as f:
        pub_pem = f.read()

    headers = {}
    if PI_REGISTRATION_TOKEN:
        headers["X-Pi-Registration-Token"] = PI_REGISTRATION_TOKEN

    try:
        r = requests.post(
            f"{BACKEND_URL}/presence/pi/register",
            json={"pi_id": PI_ID, "public_key_pem": pub_pem},
            headers=headers,
            timeout=5,
        )
        if r.status_code == 200:
            print(f"Registered public key for {PI_ID}")
        else:
            print(f"Public key registration failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Public key registration error: {e}")

if __name__ == "__main__":
    stop_evt = threading.Event()
    _register_public_key()
    threading.Thread(target=_heartbeat_loop, args=(stop_evt,), daemon=True).start()

    print(f"Starting Pi bridge for {PI_ID} on http://{RPI_BRIDGE_HOST}:{RPI_BRIDGE_PORT}")
    print(f"Heartbeat -> {BACKEND_URL}/presence/pi/heartbeat every {HEARTBEAT_INTERVAL_SECONDS}s")
    print(f"Advertised bridge URL: {_bridge_url()}")
    print("Endpoints: GET /health, GET /challenge")
    try:
        app.run(host=RPI_BRIDGE_HOST, port=RPI_BRIDGE_PORT, debug=False)
    finally:
        stop_evt.set()
