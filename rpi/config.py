import os

BACKEND_URL = os.getenv("BACKEND_URL", "https://jwt-verification-sk0m.onrender.com").rstrip("/")

# Optional override. Leave empty to auto-generate/persist a stable pi_id.
PI_ID = os.getenv("PI_ID", "").strip()
RPI_BRIDGE_HOST = os.getenv("RPI_BRIDGE_HOST", "0.0.0.0").strip()
RPI_BRIDGE_PORT = int(os.getenv("RPI_BRIDGE_PORT", "8080"))
RPI_BRIDGE_ADVERTISED_URL = os.getenv("RPI_BRIDGE_ADVERTISED_URL", "").strip()
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "10"))
PI_REGISTRATION_TOKEN = os.getenv("PI_REGISTRATION_TOKEN", "").strip()
ALLOW_CTRNG_FALLBACK = os.getenv("ALLOW_CTRNG_FALLBACK", "true").lower() == "true"

JWT_ALGORITHM = "RS256"
