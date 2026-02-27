import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ed25519

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USER_KEYS = {
    "user1": f"{BASE_DIR}/keys/user_keys/user1_pub.pem"
}
USER_ED25519_PUB_HEX = {
    "user1": os.getenv(
        "USER1_ED25519_PUBLIC_KEY_HEX",
        "c5b632629faa0428e85a1647b4ce25044defbf0c7681f1b4861764a2b14564ad"
    )
}

def verify_user_signature(user_id, message: bytes, signature: bytes):
    ed_pub_hex = USER_ED25519_PUB_HEX.get(user_id, "")
    if ed_pub_hex:
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(ed_pub_hex)
        )
        pub_key.verify(signature, message)
        return

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
