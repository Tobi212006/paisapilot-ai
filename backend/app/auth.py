"""Validate Supabase sessions server-side; never accept a client-supplied owner id."""
import os
import httpx
from fastapi import Header, HTTPException
from .config import demo_allowed


def auth_config():
    return os.getenv("SUPABASE_URL", "").rstrip("/"), os.getenv("SUPABASE_PUBLISHABLE_KEY", "")


async def owner_id(authorization: str | None = Header(default=None)) -> str:
    url, key = auth_config()
    if not url and not key and demo_allowed():
        # Explicit shared demo mode, only suitable for a loopback development server.
        return "demo"
    if not url or not key:
        raise HTTPException(503, "Account service configuration is incomplete.")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in to access your private workspace.")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{url}/auth/v1/user", headers={"apikey": key, "Authorization": authorization})
        if response.status_code in (401, 403):
            raise HTTPException(401, "Your session expired. Please sign in again.")
        response.raise_for_status()
        user = response.json()
        if not isinstance(user, dict) or not isinstance(user.get("id"), str) or not user["id"].strip():
            raise ValueError("Missing identity")
        return str(user["id"])
    except HTTPException:
        raise
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(503, "Account verification is temporarily unavailable.")
