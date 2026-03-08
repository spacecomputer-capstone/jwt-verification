"""
Legacy development/testing route.

This file supported an older presence-start flow during development. It is not
part of the current JWT workflow because the active flow uses the Pi challenge
exchange endpoint instead, and this blueprint is not registered in the app.
"""

from flask import Blueprint, jsonify

bp = Blueprint("presence_start", __name__)


@bp.route("/presence/start", methods=["POST"])
def start_presence():
    return jsonify({
        "error": "Deprecated. Use POST /presence/exchange via Pi challenge flow."
    }), 410
