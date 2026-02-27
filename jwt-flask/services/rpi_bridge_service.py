import os
import requests
from config import PI_BRIDGE_URL_TEMPLATE


def _bridge_base_for_pi(pi_id: str) -> str:
    env_key = f"PI_BRIDGE_URL_{pi_id.upper()}"
    mapped = os.getenv(env_key)
    if mapped:
        return mapped.rstrip("/")
    if PI_BRIDGE_URL_TEMPLATE:
        return PI_BRIDGE_URL_TEMPLATE.format(pi_id=pi_id).rstrip("/")
    raise Exception(f"No bridge URL configured for {pi_id}")


def fetch_signed_challenge(pi_id: str, user_id: str) -> dict:
    base = _bridge_base_for_pi(pi_id)
    r = requests.get(
        f"{base}/challenge",
        params={"pi_id": pi_id, "user_id": user_id},
        timeout=5
    )

    if r.status_code != 200:
        raise Exception(f"Pi bridge error {r.status_code}: {r.text}")

    payload = r.json()
    challenge = payload.get("challenge")
    pi_signature = payload.get("pi_signature")
    actual_pi_id = payload.get("pi_id") or pi_id
    if not challenge or not pi_signature:
        raise Exception("Pi bridge returned incomplete challenge payload")

    return {
        "user_id": user_id,
        "pi_id": actual_pi_id,
        "challenge": challenge,
        "pi_signature": pi_signature,
    }
