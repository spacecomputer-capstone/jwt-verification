from datetime import datetime, timezone
from models import db
from models.pi_status import PiStatus


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _get_or_create(pi_id: str) -> PiStatus:
    status = PiStatus.query.filter_by(pi_id=pi_id).first()
    if status:
        return status
    status = PiStatus(pi_id=pi_id)
    db.session.add(status)
    return status


def upsert_heartbeat(pi_id: str, bridge_url: str | None, status_text: str | None, error_text: str | None):
    status = _get_or_create(pi_id)
    status.last_seen = _utcnow()
    status.bridge_url = bridge_url or status.bridge_url
    status.last_status = status_text or "online"
    status.last_error = error_text
    db.session.commit()


def mark_challenge(pi_id: str):
    status = _get_or_create(pi_id)
    status.last_challenge_at = _utcnow()
    db.session.commit()


def mark_exchange(pi_id: str):
    status = _get_or_create(pi_id)
    status.last_exchange_at = _utcnow()
    db.session.commit()
