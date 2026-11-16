import os
import json
import base64
from urllib.parse import urlsplit


def production():
    return os.getenv("APP_ENV", "development").lower() == "production"


def demo_allowed():
    return not production() and os.getenv("DEMO_MODE", "true").lower() == "true"


def validate_configuration():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if bool(url) != bool(key):
        raise RuntimeError("Set both Supabase project settings, or remove both for local demo mode.")
    if url:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise RuntimeError("SUPABASE_URL must be an HTTPS project origin.")
    secret_key = key.startswith("sb_secret_")
    try:
        payload = key.split(".")[1]
        secret_key = secret_key or json.loads(base64.urlsafe_b64decode(payload + "="*(-len(payload)%4))).get("role") == "service_role"
    except (IndexError, ValueError, TypeError, AttributeError):
        pass
    if secret_key:
        raise RuntimeError("Use a Supabase publishable/anon key, not a secret service key.")
    if production():
        if not url or not key or os.getenv("DEMO_MODE", "false").lower() != "false":
            raise RuntimeError("Production requires Supabase authentication and DEMO_MODE=false.")
        if not os.getenv("DATABASE_PATH") or not os.getenv("CORS_ORIGINS"):
            raise RuntimeError("Production requires an explicit database path and CORS origins.")
        origins = [x.strip() for x in os.environ["CORS_ORIGINS"].split(",")]
        if any(not x.startswith("https://") or "*" in x for x in origins):
            raise RuntimeError("Production CORS origins must be explicit HTTPS origins.")
