import os
import secrets
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import PI_ID, RPI_BRIDGE_HOST, RPI_BRIDGE_PORT

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)

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

    c_trng = secrets.token_hex(16)
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
