import os
from dotenv import load_dotenv

load_dotenv()

JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", 60))
REQUIRE_USER_SIGNATURE = os.getenv("REQUIRE_USER_SIGNATURE", "true").lower() == "true"
PI_BRIDGE_URL_TEMPLATE = os.getenv("PI_BRIDGE_URL_TEMPLATE", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

BASE_DIR = os.path.dirname(__file__)

def _env_or_file(env_name: str, fallback_path: str) -> str:
    env_value = os.getenv(env_name)
    if env_value:
        return env_value.replace("\\n", "\n")
    with open(fallback_path, "r", encoding="utf-8") as f:
        return f.read()

BACKEND_PRIVATE_KEY = _env_or_file(
    "BACKEND_PRIVATE_KEY",
    f"{BASE_DIR}/keys/backend_private.pem"
)
BACKEND_PUBLIC_KEY = _env_or_file(
    "BACKEND_PUBLIC_KEY",
    f"{BASE_DIR}/keys/backend_public.pem"
)

SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
