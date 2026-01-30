import jwt
import time
import os
import hashlib
import secrets
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import BACKEND_URL, PI_ID
import asyncio
from ble_listener import JWTServer

# Load keys
BASE_DIR = os.path.dirname(__file__)

with open(f"{BASE_DIR}/keys/backend_public.pem", "rb") as f:
    BACKEND_PUBLIC_KEY = f.read()

with open(f"{BASE_DIR}/keys/pi_private.pem", "rb") as f:
    PI_PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Verify backend JWT
def verify_presence_jwt(token):
    return jwt.decode(
        token,
        BACKEND_PUBLIC_KEY,
        algorithms=["RS256"]
    )

# Rapid challenge rounds
def run_challenge_rounds(m=20):
    """
    Simulated rounds.
    Replace with BLE logic later.
    """
    transcript = []
    success = 0

    for i in range(m):
        ci = secrets.token_bytes(16)   # cTRNG-like
        start = time.monotonic()

        # simulate phone response
        ri = hashlib.sha256(ci).digest()

        dt = time.monotonic() - start

        transcript.append((ci.hex(), ri.hex(), dt))

        if dt < 0.05:  # 50ms threshold
            success += 1

    return transcript, success

# Sign attestation
def sign_attestation(message: bytes):
    return PI_PRIVATE_KEY.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

# Main flow
def handle_presence_token(presence_jwt):
    # 1. verify JWT
    claims = verify_presence_jwt(presence_jwt)

    if claims["pid"] != PI_ID:
        print("Wrong Pi ID")
        return

    print("JWT valid. Running challenge rounds...")

    # 2. rounds
    transcript, success = run_challenge_rounds()

    transcript_str = str(transcript)
    transcript_hash = hashlib.sha256(transcript_str.encode()).hexdigest()

    # 3. sign
    signature = sign_attestation(transcript_str.encode())

    # 4. send to backend
    payload = {
        "presence_jwt": presence_jwt,
        "attestation": transcript_str,
        "signature": signature.hex()
    }

    r = requests.post(f"{BACKEND_URL}/presence/verify", json=payload)

    print("Backend response:", r.json())

def on_token_received(token):
    handle_presence_token(token)

# Simulated BLE entrypoint
if __name__ == "__main__":
    server = JWTServer(on_token_received)
    asyncio.run(server.start())