import os
import subprocess
import secrets
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import RPI_BRIDGE_HOST, RPI_BRIDGE_PORT, ALLOW_CTRNG_FALLBACK
from pi_identity import get_pi_id

app = Flask(__name__)
PI_ID = get_pi_id()

BASE_DIR = os.path.dirname(__file__)
CTRNG_SCRIPT = os.path.join(BASE_DIR, "scripts", "get_ctrng.mjs")

with open(f"{BASE_DIR}/keys/pi_private.pem", "rb") as f:
    PI_PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


def _sign_with_pi(message: bytes) -> bytes:
    return PI_PRIVATE_KEY.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def _ctrng_hex() -> str:
    # Source challenge via Orbitport SDK (Node/TS path), not Python RNG.
    proc = subprocess.run(
        ["node", CTRNG_SCRIPT],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "unknown error").strip()
        if ALLOW_CTRNG_FALLBACK:
            return secrets.token_hex(16)
        raise Exception(f"Orbitport cTRNG failed: {err}")

    value = proc.stdout.strip().lower()
    if len(value) < 32:
        if ALLOW_CTRNG_FALLBACK:
            return secrets.token_hex(16)
        raise Exception("Orbitport cTRNG returned insufficient bytes")
    # Use 16-byte challenge hex expected by current protocol.
    return value[:32]


@app.get("/health")
def health():
    return jsonify({"ok": True, "pi_id": PI_ID})


@app.get("/challenge")
def challenge():
    user_id = request.args.get("user_id", "user1")
    requested_pi_id = request.args.get("pi_id", PI_ID)
    if requested_pi_id != PI_ID:
        return jsonify({
            "ok": False,
            "error": f"Pi ID mismatch: requested={requested_pi_id}, actual={PI_ID}"
        }), 400

    c_trng = _ctrng_hex()
    pi_sig = _sign_with_pi(c_trng.encode()).hex()

    return jsonify({
        "ok": True,
        "user_id": user_id,
        "pi_id": PI_ID,
        "challenge": c_trng,
        "pi_signature": pi_sig,
    })


if __name__ == "__main__":
    app.run(host=RPI_BRIDGE_HOST, port=RPI_BRIDGE_PORT, debug=False)
