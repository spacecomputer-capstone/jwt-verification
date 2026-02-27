from models import db
from models.pi_key import PiKey


def upsert_pi_key(pi_id: str, public_key_pem: str):
    row = PiKey.query.filter_by(pi_id=pi_id).first()
    if row:
        row.public_key_pem = public_key_pem
    else:
        row = PiKey(pi_id=pi_id, public_key_pem=public_key_pem)
        db.session.add(row)
    db.session.commit()
    return row
