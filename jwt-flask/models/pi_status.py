from . import db


class PiStatus(db.Model):
    pi_id = db.Column(db.String, primary_key=True)
    bridge_url = db.Column(db.String, nullable=True)
    last_status = db.Column(db.String, nullable=True)
    last_error = db.Column(db.String, nullable=True)

    last_seen = db.Column(db.DateTime, nullable=True)
    last_challenge_at = db.Column(db.DateTime, nullable=True)
    last_exchange_at = db.Column(db.DateTime, nullable=True)

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
