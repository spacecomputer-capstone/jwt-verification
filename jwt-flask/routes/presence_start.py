from flask import Blueprint, jsonify

bp = Blueprint("presence_start", __name__)


@bp.route("/presence/start", methods=["POST"])
def start_presence():
    return jsonify({
        "error": "Deprecated. Use POST /presence/exchange via Pi challenge flow."
    }), 410
