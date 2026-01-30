from models import db
from models.proof import PresenceProof

def store_proof(uid, pid, sid, success, transcript_hash):
    proof = PresenceProof(
        user_id=uid,
        pi_id=pid,
        sid=sid,
        success=success,
        transcript_hash=transcript_hash
    )
    db.session.add(proof)
    db.session.commit()