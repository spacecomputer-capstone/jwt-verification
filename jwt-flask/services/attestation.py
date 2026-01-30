from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PI_KEYS = {
    "pi1": f"{BASE_DIR}/keys/pi_keys/pi1_pub.pem"
}

def verify_pi_signature(pi_id, message: bytes, signature: bytes):
    path = PI_KEYS.get(pi_id)

    if not path:
        raise Exception("Unknown Pi")

    with open(path, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())

    pub_key.verify(
        signature,
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
