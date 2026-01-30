from flask import Blueprint, request, jsonify
from services.jwt_service import issue_presence_token

bp = Blueprint("presence_start", __name__)


@bp.route("/presence/start", methods=["POST"])
def start_presence():
    data = request.json

    user_id = data["user_id"]
    pi_id = data["pi_id"]

    token = issue_presence_token(user_id, pi_id)

    return jsonify({"presence_jwt": token})