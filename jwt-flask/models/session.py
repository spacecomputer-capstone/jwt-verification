from . import db

class PresenceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    pi_id = db.Column(db.String, nullable=False)
    sid = db.Column(db.String, unique=True, nullable=False)
    challenge_hash = db.Column(db.String, unique=True, nullable=False)
    jwt_token = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
