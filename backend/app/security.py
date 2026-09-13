from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request

from .settings import settings


def require_owner(x_admin_token: str = Header(default="")) -> str:
    if not settings.admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(status_code=401, detail="Owner authentication required")
    return "owner"


def require_mutation_guard(
    request: Request,
    x_admin_token: str = Header(default=""),
    x_csrf_token: str = Header(default=""),
) -> str:
    require_owner(x_admin_token)
    if not hmac.compare_digest(x_csrf_token, x_admin_token):
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Origin is not allowed")
    return "owner"


FORBIDDEN_PATTERNS = ("ignore previous", "system prompt", "api key", "run shell", "drop table")


def validate_prompt(text: str) -> None:
    normalized = text.lower()
    if any(pattern in normalized for pattern in FORBIDDEN_PATTERNS):
        raise HTTPException(status_code=400, detail="Question contains a forbidden instruction")
