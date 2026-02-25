from flask import Blueprint, request, jsonify
from services.jwt_service import issue_presence_token
from services.attestation import verify_pi_signature
from services.user_identity import verify_user_signature
from services.db_service import store_session

bp = Blueprint("presence_exchange", __name__)

def _required(data, keys):
    missing = [k for k in keys if k not in data]
    if missing:
        return f"Missing fields: {', '.join(missing)}"
    return None

@bp.route("/presence/exchange", methods=["POST"])
def presence_exchange():
    data = request.get_json(silent=True) or {}

    err = _required(
        data,
        ["user_id", "pi_id", "challenge", "pi_signature", "user_signature"]
    )
    if err:
        return jsonify({"error": err}), 400

    user_id = data["user_id"]
    pi_id = data["pi_id"]
    challenge = data["challenge"]

    try:
        pi_sig = bytes.fromhex(data["pi_signature"])
        user_sig = bytes.fromhex(data["user_signature"])
    except ValueError:
        return jsonify({"error": "Signatures must be hex-encoded bytes"}), 400

    challenge_bytes = challenge.encode()

    try:
        verify_pi_signature(pi_id, challenge_bytes, pi_sig)
        verify_user_signature(user_id, challenge_bytes, user_sig)
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    token, sid = issue_presence_token(user_id, pi_id)

    try:
        store_session(user_id, pi_id, sid, challenge, token)
    except Exception:
        # Prevent silent replay/session duplication issues on DB constraints
        return jsonify({"error": "Session replay or duplicate detected"}), 409

    return jsonify({"presence_jwt": token, "sid": sid})
