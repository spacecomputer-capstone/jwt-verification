import os
import subprocess
import secrets
import threading
import time
from collections import deque
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import RPI_BRIDGE_HOST, RPI_BRIDGE_PORT, ALLOW_CTRNG_FALLBACK
from pi_identity import get_pi_id

app = Flask(__name__)
PI_ID = get_pi_id()

BASE_DIR = os.path.dirname(__file__)
CTRNG_SCRIPT = os.path.join(BASE_DIR, "scripts", "get_ctrng.mjs")
CTRNG_TIMEOUT_SECONDS = float(os.getenv("CTRNG_TIMEOUT_SECONDS", "1.2"))
CHALLENGE_CACHE_SIZE = int(os.getenv("CHALLENGE_CACHE_SIZE", "4"))
CHALLENGE_MAX_AGE_SECONDS = float(os.getenv("CHALLENGE_MAX_AGE_SECONDS", "20"))
REFILL_SLEEP_SECONDS = 0.15

_CACHE_LOCK = threading.Lock()
_CHALLENGE_CACHE = deque()

with open(f"{BASE_DIR}/keys/pi_private.pem", "rb") as f:
    PI_PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


def _generate_signed_packet() -> dict:
    challenge_hex = _ctrng_hex()
    return {
        "challenge": challenge_hex,
        "pi_signature": _sign_with_pi(challenge_hex.encode()).hex(),
        "generated_at": time.time(),
    }


def _get_cached_signed_packet() -> dict:
    now = time.time()
    with _CACHE_LOCK:
        while _CHALLENGE_CACHE:
            packet = _CHALLENGE_CACHE.popleft()
            if now - packet["generated_at"] <= CHALLENGE_MAX_AGE_SECONDS:
                return packet

    # Cache miss/stale: generate synchronously.
    return _generate_signed_packet()


def _refill_cache_forever():
    while True:
        try:
            with _CACHE_LOCK:
                need_refill = len(_CHALLENGE_CACHE) < CHALLENGE_CACHE_SIZE

            if not need_refill:
                time.sleep(REFILL_SLEEP_SECONDS)
                continue

            packet = _generate_signed_packet()
            with _CACHE_LOCK:
                if len(_CHALLENGE_CACHE) < CHALLENGE_CACHE_SIZE:
                    _CHALLENGE_CACHE.append(packet)
        except Exception:
            # Keep bridge alive even if cTRNG provider is unstable.
            time.sleep(REFILL_SLEEP_SECONDS)


def _sign_with_pi(message: bytes) -> bytes:
    return PI_PRIVATE_KEY.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def _ctrng_hex() -> str:
    # Source challenge via Orbitport SDK (Node/TS path), not Python RNG.
    try:
        proc = subprocess.run(
            ["node", CTRNG_SCRIPT],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=CTRNG_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        if ALLOW_CTRNG_FALLBACK:
            return secrets.token_hex(16)
        raise Exception(f"Orbitport cTRNG timed out after {CTRNG_TIMEOUT_SECONDS}s") from e
    except Exception as e:
        if ALLOW_CTRNG_FALLBACK:
            return secrets.token_hex(16)
        raise Exception(f"Orbitport cTRNG invocation failed: {e}") from e
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
    requested_pi_id = request.args.get("pi_id", "").strip()

    # Accept mismatched or empty requested pi_id to keep app flow robust across
    # different mascot mappings; always return this bridge's canonical PI_ID.
    packet = _get_cached_signed_packet()
    c_trng = packet["challenge"]
    pi_sig = packet["pi_signature"]

    return jsonify({
        "ok": True,
        "user_id": user_id,
        "pi_id": PI_ID,
        "requested_pi_id": requested_pi_id or None,
        "challenge": c_trng,
        "pi_signature": pi_sig,
    })


threading.Thread(target=_refill_cache_forever, daemon=True).start()


if __name__ == "__main__":
    app.run(host=RPI_BRIDGE_HOST, port=RPI_BRIDGE_PORT, debug=False)
