import json
import os
import secrets
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import BACKEND_URL, PI_ID

BASE_DIR = os.path.dirname(__file__)

with open(f"{BASE_DIR}/keys/pi_private.pem", "rb") as f:
    PI_PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


def sign_with_pi(message: bytes) -> bytes:
    return PI_PRIVATE_KEY.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def issue_signed_challenge():
    challenge = secrets.token_hex(16)
    pi_signature = sign_with_pi(challenge.encode())
    return challenge, pi_signature


def request_jwt_from_backend(user_id: str, challenge: str, pi_sig: bytes, user_sig_hex: str):
    payload = {
        "user_id": user_id,
        "pi_id": PI_ID,
        "challenge": challenge,
        "pi_signature": pi_sig.hex(),
        "user_signature": user_sig_hex,
    }

    response = requests.post(
        f"{BACKEND_URL}/presence/exchange",
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response.json()["presence_jwt"]


def run_access_flow(user_id="user1"):
    print(f'User -> Pi: "I want access to resources" (user={user_id})')

    challenge, pi_sig = issue_signed_challenge()
    print('Pi -> User: "Challenge cTRNG with Pi signature"')

    challenge_packet = {
        "user_id": user_id,
        "challenge": challenge,
        "pi_signature": pi_sig.hex()
    }
    print("\nSend this packet to user client:")
    print(json.dumps(challenge_packet, indent=2))

    user_sig_hex = input("\nPaste `user_signature` from user client: ").strip()
    print('User -> Pi: "Signed cTRNG"')

    print('Pi -> Backend: "Forward signed challenge info"')
    jwt_token = request_jwt_from_backend(user_id, challenge, pi_sig, user_sig_hex)

    print('Backend -> Pi: "Forward JWT"')
    print('Pi -> User: "Forward JWT"')
    print("\nJWT:")
    print(jwt_token)


if __name__ == "__main__":
    run_access_flow("user1")
