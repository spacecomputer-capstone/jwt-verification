import json
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE_DIR = os.path.dirname(__file__)

with open(f"{BASE_DIR}/keys/user1_private.pem", "rb") as f:
    USER1_PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

with open(f"{BASE_DIR}/keys/pi_public.pem", "rb") as f:
    PI_PUBLIC_KEY = serialization.load_pem_public_key(f.read())


def verify_pi_signature(challenge: str, pi_signature_hex: str) -> None:
    PI_PUBLIC_KEY.verify(
        bytes.fromhex(pi_signature_hex),
        challenge.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def sign_challenge(challenge: str) -> str:
    signature = USER1_PRIVATE_KEY.sign(
        challenge.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature.hex()


def run_user_flow():
    print('Pi -> User: paste challenge packet JSON from Pi client')
    packet_raw = input("challenge_packet JSON: ").strip()
    packet = json.loads(packet_raw)

    user_id = packet["user_id"]
    challenge = packet["challenge"]
    pi_signature = packet["pi_signature"]

    verify_pi_signature(challenge, pi_signature)

    if user_id != "user1":
        raise Exception("This demo user client only supports user1")

    user_signature = sign_challenge(challenge)
    print('User -> Pi: signed cTRNG generated')
    print(f"user_signature={user_signature}")


if __name__ == "__main__":
    run_user_flow()
