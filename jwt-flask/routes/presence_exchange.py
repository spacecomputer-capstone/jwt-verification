import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from cryptography.exceptions import InvalidSignature
from services.jwt_service import issue_presence_token
from services.attestation import verify_pi_signature
from services.user_identity import verify_user_signature
from services.db_service import store_session
from services.rpi_bridge_service import fetch_signed_challenge
from services.pi_status_service import mark_challenge, mark_exchange
from config import REQUIRE_USER_SIGNATURE

bp = Blueprint("presence_exchange", __name__)


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short(value: str, keep: int = 24) -> str:
    if not value:
        return ""
    if len(value) <= keep:
        return value
    return f"{value[:keep]}...({len(value)} chars)"


def _demo_log(event: str, payload: dict):
    print(f"[DEMO][{_ts()}][BACKEND][{event}] {json.dumps(payload, separators=(',', ':'))}")


def _required(data, keys):
    missing = [k for k in keys if k not in data]
    if missing:
        return f"Missing fields: {', '.join(missing)}"
    return None


@bp.route("/presence/challenge", methods=["GET"])
def presence_challenge():
    user_id = request.args.get("user_id", "user1")
    pi_id = request.args.get("pi_id", "")
    if not pi_id:
        return jsonify({"error": "Missing pi_id"}), 400

    try:
        packet = fetch_signed_challenge(pi_id, user_id)
        mark_challenge(packet["pi_id"])
        _demo_log("challenge_forward", {
            "user_id": user_id,
            "requested_pi_id": pi_id,
            "resolved_pi_id": packet.get("pi_id"),
            "challenge": packet.get("challenge"),
            "pi_signature_preview": _short(packet.get("pi_signature", "")),
        })
        return jsonify(packet)
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@bp.route("/presence/exchange", methods=["POST"])
def presence_exchange():
    data = request.get_json(silent=True) or {}

    required_fields = ["user_id", "pi_id", "challenge", "pi_signature"]
    if REQUIRE_USER_SIGNATURE:
        required_fields.append("user_signature")

    err = _required(
        data,
        required_fields
    )
    if err:
        return jsonify({"error": err}), 400

    user_id = data["user_id"]
    pi_id = data["pi_id"]
    challenge = data["challenge"]
    # App currently fetches challenge directly from Pi bridge, so reflect challenge
    # activity here for admin visibility even when /presence/challenge is bypassed.
    mark_challenge(pi_id)
    _demo_log("exchange_request", {
        "user_id": user_id,
        "pi_id": pi_id,
        "challenge": challenge,
        "pi_signature_preview": _short(data.get("pi_signature", "")),
        "user_signature_preview": _short(data.get("user_signature", "")),
    })

    try:
        pi_sig = bytes.fromhex(data["pi_signature"])
        user_sig_hex = data.get("user_signature", "")
        user_sig = bytes.fromhex(user_sig_hex) if user_sig_hex else None
    except ValueError:
        return jsonify({"error": "Signatures must be hex-encoded bytes"}), 400

    challenge_bytes = challenge.encode()

    try:
        verify_pi_signature(pi_id, challenge_bytes, pi_sig)
        _demo_log("pi_verify_ok", {"pi_id": pi_id, "challenge": challenge})
    except InvalidSignature:
        return jsonify({"error": "Invalid Pi signature"}), 401
    except Exception as e:
        return jsonify({"error": f"Pi verify error: {e}"}), 401

    if REQUIRE_USER_SIGNATURE:
        if not user_sig:
            return jsonify({"error": "Missing user signature"}), 400
        try:
            verify_user_signature(user_id, challenge_bytes, user_sig)
            _demo_log("user_verify_ok", {"user_id": user_id, "challenge": challenge})
        except InvalidSignature:
            return jsonify({"error": "Invalid user signature"}), 401
        except Exception as e:
            return jsonify({"error": f"User verify error: {e}"}), 401

    token, sid = issue_presence_token(user_id, pi_id)

    try:
        session, created = store_session(user_id, pi_id, sid, challenge, token)
        mark_exchange(pi_id)
    except Exception:
        # Prevent silent replay/session duplication issues on DB constraints
        return jsonify({"error": "Session replay or duplicate detected"}), 409

    if not created:
        _demo_log("jwt_reused", {
            "user_id": user_id,
            "pi_id": pi_id,
            "sid": session.sid,
            "reused": True,
            "jwt_preview": _short(session.jwt_token),
        })
        return jsonify({"presence_jwt": session.jwt_token, "sid": session.sid, "reused": True})

    _demo_log("jwt_issued", {
        "user_id": user_id,
        "pi_id": pi_id,
        "sid": sid,
        "reused": False,
        "jwt_preview": _short(token),
    })
    return jsonify({"presence_jwt": token, "sid": sid, "reused": False})
