import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USER_KEYS = {
    "user1": f"{BASE_DIR}/keys/user_keys/user1_pub.pem"
}

def verify_user_signature(user_id, message: bytes, signature: bytes):
    path = USER_KEYS.get(user_id)

    if not path:
        raise Exception("Unknown user")

    with open(path, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())

    pub_key.verify(
        signature,
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
