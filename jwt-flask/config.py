import os
from dotenv import load_dotenv

load_dotenv()

JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", 60))

BASE_DIR = os.path.dirname(__file__)

BACKEND_PRIVATE_KEY = os.getenv("BACKEND_PRIVATE_KEY").replace("\\n", "\n") or open(f"{BASE_DIR}/keys/backend_private.pem").read()
BACKEND_PUBLIC_KEY = os.getenv("BACKEND_PUBLIC_KEY").replace("\\n", "\n") or open(f"{BASE_DIR}/keys/backend_public.pem").read()

SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"