import hashlib
from models import db
from models.proof import PresenceProof
from models.session import PresenceSession

def store_proof(uid, pid, sid, success, transcript_hash):
    proof = PresenceProof(
        user_id=uid,
        pi_id=pid,
        sid=sid,
        success=success,
        transcript_hash=transcript_hash
    )
    db.session.add(proof)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

def store_session(uid, pid, sid, challenge, jwt_token):
    challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()
    session = PresenceSession(
        user_id=uid,
        pi_id=pid,
        sid=sid,
        challenge_hash=challenge_hash,
        jwt_token=jwt_token,
    )
    db.session.add(session)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise