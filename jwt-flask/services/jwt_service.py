import jwt
import time
import uuid
from config import BACKEND_PRIVATE_KEY, BACKEND_PUBLIC_KEY, JWT_EXP_SECONDS

def issue_presence_token(user_id, pi_id):
    sid = str(uuid.uuid4())
    payload = {
        "uid": user_id,
        "pid": pi_id,
        "sid": sid,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECONDS,
    }
    token = jwt.encode(payload, BACKEND_PRIVATE_KEY, algorithm="RS256")
    return token, sid

def verify_presence_token(token):
    return jwt.decode(token, BACKEND_PUBLIC_KEY, algorithms=["RS256"])
