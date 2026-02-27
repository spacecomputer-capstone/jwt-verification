from . import db


class PiKey(db.Model):
    pi_id = db.Column(db.String, primary_key=True)
    public_key_pem = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
