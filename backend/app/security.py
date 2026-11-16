"""Single-process request guardrails; use a trusted reverse proxy for distributed limits."""
import logging
import time
import uuid
import os
from .config import production
from collections import OrderedDict
from starlette.responses import JSONResponse

logger = logging.getLogger("paisapilot.requests")


class RequestGuards:
    def __init__(self, app, max_body=300_000, limit=180):
        self.app, self.max_body, self.limit = app, max_body, limit
        self.windows = OrderedDict()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = uuid.uuid4().hex
        started = time.monotonic()
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        path = scope.get("path", "")
        status = 500
        response_started = False

        async def wrapped_send(message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status = message["status"]
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", request_id.encode()),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                ]
                if path.startswith("/api/"):
                    message["headers"].append((b"cache-control", b"no-store"))
                if production():
                    account_origin = os.getenv("SUPABASE_URL", "").rstrip("/")
                    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: blob:; connect-src 'self' " + account_origin + "; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
                    message["headers"] += [(b"content-security-policy", csp.encode()), (b"strict-transport-security", b"max-age=31536000")]
            await send(message)

        async def reject(code, detail, extra=None):
            response = JSONResponse({"detail": detail, "request_id": request_id}, status_code=code, headers=extra)
            await response(scope, receive, wrapped_send)

        if path.startswith("/api/"):
            # Never trust arbitrary X-Forwarded-For from visitors.
            identity = (scope.get("client") or ("unknown",))[0]
            now = time.monotonic()
            window, count = self.windows.get(identity, (now, 0))
            if now - window >= 60:
                window, count = now, 0
            self.windows[identity] = (window, count + 1)
            self.windows.move_to_end(identity)
            while len(self.windows) > 2048:
                self.windows.popitem(last=False)
            if count >= self.limit:
                return await reject(429, "Too many requests. Try again in a minute.", {"Retry-After": "60"})
        try:
            declared = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await reject(400, "Invalid content length.")
        if declared > self.max_body:
            return await reject(413, "Request is too large. Use at most 300 KB.")
        if scope["method"] in ("POST", "PUT", "PATCH"):
            if not headers.get(b"content-type", b"").split(b";")[0].strip().lower() == b"application/json":
                return await reject(415, "Send an application/json request.")
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > self.max_body:
                    return await reject(413, "Request is too large. Use at most 300 KB.")
                if not message.get("more_body"):
                    break
            delivered = False

            async def buffered_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()
        else:
            buffered_receive = receive
        try:
            await self.app(scope, buffered_receive, wrapped_send)
        except Exception:
            # Do not log bodies, bearer tokens, full URLs or user financial records.
            logger.error("request_failed id=%s method=%s", request_id, scope["method"])
            if not response_started:
                await reject(500, "An internal error occurred. Quote the request id when reporting it.")
            else:
                raise
        finally:
            logger.info("request id=%s method=%s status=%s duration_ms=%d", request_id, scope["method"], status, int((time.monotonic()-started)*1000))
