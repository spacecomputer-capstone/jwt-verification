"""
Legacy development/testing route.

This file was used for an earlier presence verification step that stored proof
records after JWT validation. It is not part of the current JWT workflow
because this blueprint is not registered in the active Flask app.
"""

from flask import Blueprint, request, jsonify
from services.jwt_service import verify_presence_token
from services.attestation import verify_pi_signature
from services.db_service import store_proof

import hashlib

bp = Blueprint("presence_verify", __name__)

@bp.route("/presence/verify", methods=["POST"])
def verify_presence():
    data = request.json

    token = data["presence_jwt"]
    attestation = data["attestation"]
    signature = bytes.fromhex(data["signature"])

    claims = verify_presence_token(token)

    verify_pi_signature(
        claims["pid"],
        attestation.encode(),
        signature
    )

    transcript_hash = hashlib.sha256(attestation.encode()).hexdigest()

    store_proof(
        claims["uid"],
        claims["pid"],
        claims["sid"],
        True,
        transcript_hash
    )

    return jsonify({"status": "PASS"})
