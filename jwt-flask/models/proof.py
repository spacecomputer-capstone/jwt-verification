from . import db

class PresenceProof(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String)
    pi_id = db.Column(db.String)
    sid = db.Column(db.String)

    success = db.Column(db.Boolean)
    transcript_hash = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default=db.func.now())