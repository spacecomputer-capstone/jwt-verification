from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request, Response
from config import ADMIN_TOKEN, PI_REGISTRATION_TOKEN
from models.pi_status import PiStatus
from services.pi_status_service import upsert_heartbeat
from services.pi_key_service import upsert_pi_key

bp = Blueprint("admin_pi", __name__)


def _authorized() -> bool:
    if not ADMIN_TOKEN:
        return True
    header = request.headers.get("X-Admin-Token", "")
    query = request.args.get("token", "")
    return header == ADMIN_TOKEN or query == ADMIN_TOKEN


def _require_admin():
    if not _authorized():
        return jsonify({"error": "Unauthorized"}), 401
    return None


def _registration_authorized() -> bool:
    if not PI_REGISTRATION_TOKEN:
        return True
    header = request.headers.get("X-Pi-Registration-Token", "")
    return header == PI_REGISTRATION_TOKEN


@bp.route("/presence/pi/heartbeat", methods=["POST"])
def pi_heartbeat():
    data = request.get_json(silent=True) or {}
    pi_id = data.get("pi_id", "").strip()
    if not pi_id:
        return jsonify({"error": "Missing pi_id"}), 400

    upsert_heartbeat(
        pi_id=pi_id,
        bridge_url=data.get("bridge_url"),
        status_text=data.get("status", "online"),
        error_text=data.get("error"),
    )
    return jsonify({"ok": True})


@bp.route("/presence/pi/register", methods=["POST"])
def pi_register():
    if not _registration_authorized():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    pi_id = data.get("pi_id", "").strip()
    public_key_pem = data.get("public_key_pem", "").strip()

    if not pi_id or not public_key_pem:
        return jsonify({"error": "Missing pi_id or public_key_pem"}), 400

    upsert_pi_key(pi_id, public_key_pem)
    return jsonify({"ok": True, "pi_id": pi_id})


@bp.route("/presence/pi/resolve", methods=["GET"])
def pi_resolve():
    pi_id = request.args.get("pi_id", "").strip()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    online_cutoff = now - timedelta(seconds=30)

    row = None
    if pi_id:
        row = PiStatus.query.filter_by(pi_id=pi_id).first()
    else:
        row = PiStatus.query.order_by(PiStatus.last_seen.desc()).first()

    if not row or not row.bridge_url:
        return jsonify({"error": "No bridge URL registered"}), 404

    online = bool(row.last_seen and row.last_seen >= online_cutoff)

    return jsonify({
        "pi_id": row.pi_id,
        "bridge_url": row.bridge_url,
        "online": online,
        "last_seen": row.last_seen.isoformat() if row.last_seen else None,
    })


@bp.route("/admin/pis", methods=["GET"])
def admin_pis_json():
    auth = _require_admin()
    if auth:
        return auth

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    online_cutoff = now - timedelta(seconds=30)

    rows = PiStatus.query.order_by(PiStatus.pi_id.asc()).all()
    payload = []
    for row in rows:
        payload.append({
            "pi_id": row.pi_id,
            "bridge_url": row.bridge_url,
            "online": bool(row.last_seen and row.last_seen >= online_cutoff),
            "last_seen": row.last_seen.isoformat() if row.last_seen else None,
            "last_status": row.last_status,
            "last_error": row.last_error,
            "last_challenge_at": row.last_challenge_at.isoformat() if row.last_challenge_at else None,
            "last_exchange_at": row.last_exchange_at.isoformat() if row.last_exchange_at else None,
        })
    return jsonify({"pis": payload})


@bp.route("/admin", methods=["GET"])
def admin_pis_html():
    auth = _require_admin()
    if auth:
        return auth

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    online_cutoff = now - timedelta(seconds=30)
    rows = PiStatus.query.order_by(PiStatus.pi_id.asc()).all()

    table_rows = []
    for row in rows:
        online = bool(row.last_seen and row.last_seen >= online_cutoff)
        status = "ONLINE" if online else "OFFLINE"
        color = "#0b7a27" if online else "#8a1d1d"
        table_rows.append(
            "<tr>"
            f"<td>{row.pi_id}</td>"
            f"<td>{status}</td>"
            f"<td>{row.bridge_url or ''}</td>"
            f"<td>{row.last_seen or ''}</td>"
            f"<td>{row.last_challenge_at or ''}</td>"
            f"<td>{row.last_exchange_at or ''}</td>"
            f"<td>{row.last_error or ''}</td>"
            "</tr>"
            .replace("<td>ONLINE</td>", f"<td style='color:{color};font-weight:700;'>ONLINE</td>")
            .replace("<td>OFFLINE</td>", f"<td style='color:{color};font-weight:700;'>OFFLINE</td>")
        )

    html = (
        "<html><head><title>Pi Admin</title>"
        "<style>body{font-family:Arial;margin:24px;}table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #ddd;padding:8px;text-align:left;}th{background:#f4f4f4;}</style>"
        "</head><body>"
        "<h2>Pi Connection Dashboard</h2>"
        "<p>Online means heartbeat within last 30 seconds.</p>"
        "<table><tr><th>Pi ID</th><th>Status</th><th>Bridge URL</th><th>Last Seen</th>"
        "<th>Last Challenge</th><th>Last Exchange</th><th>Last Error</th></tr>"
        f"{''.join(table_rows)}"
        "</table></body></html>"
    )
    return Response(html, mimetype="text/html")
