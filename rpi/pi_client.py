import json
import os
import secrets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from config import PI_ID

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


def issue_signed_challenge_packet(user_id="user1"):
    challenge = secrets.token_hex(16)
    pi_signature = sign_with_pi(challenge.encode()).hex()
    return {
        "user_id": user_id,
        "pi_id": PI_ID,
        "challenge": challenge,
        "pi_signature": pi_signature,
    }


def run_packet_emitter(user_id="user1"):
    print(f'User -> Pi: "I want access to resources" (user={user_id})')
    print('Pi -> User/App: "Challenge cTRNG with Pi signature"')

    packet = issue_signed_challenge_packet(user_id)

    print("\nPaste these values into app JWT dialog:")
    print(json.dumps(packet, indent=2))

    print("\nFor demo mode (REQUIRE_USER_SIGNATURE=false), set user_signature to empty string.")


if __name__ == "__main__":
    run_packet_emitter("user1")
