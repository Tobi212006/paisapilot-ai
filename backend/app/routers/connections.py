import os
import re
import time
from collections import OrderedDict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
import httpx
from ..services.gemini import generate
from ..auth import auth_config, owner_id
from ..config import demo_allowed
from ..services import providers

router = APIRouter(prefix="/api")


@router.get("/connections")
def connections():
    url, key = auth_config()
    return {"workspace_mode": "private" if url and key else "demo" if not url and not key and demo_allowed() else "configuration_error",
            "supabase": {"configured": bool(url and key)},
            "mutual_funds": {"configured": True, "source": "MFapi.in", "key_required": False},
            "currency": {"configured": True, "source": "Frankfurter", "key_required": False},
            "upstox": {"configured": bool(os.getenv("UPSTOX_ANALYTICS_TOKEN"))},
            "assistant": {"configured": bool(os.getenv("GEMINI_API_KEY")), "source": "Gemini", "sends_financial_records": False}}


@router.get("/funds/search")
async def funds_search(q: str = Query(min_length=2, max_length=80)):
    if len(q.strip()) < 2:
        raise HTTPException(422, "Enter at least two characters to search.")
    return await providers.fund_search(q.strip())


@router.get("/funds/{code}")
async def fund(code: int):
    if not 10000 <= code <= 99999999:
        raise HTTPException(422, "Invalid scheme code.")
    return await providers.fund_history(code)


CURRENCIES = {"INR", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "SGD", "AED", "CHF"}


@router.get("/currency")
async def currency(base: str = "USD", quote: str = "INR"):
    base, quote = base.upper(), quote.upper()
    if base not in CURRENCIES or quote not in CURRENCIES:
        raise HTTPException(422, "Choose a supported currency.")
    return await providers.exchange_rates(base, quote)


@router.get("/stocks/quote")
async def stock_quote(instrument: str = Query(min_length=3, max_length=100, pattern=r"^[A-Z0-9_ |.-]+$"), owner: str = Depends(owner_id)):
    return await providers.stock_quote(instrument)


class AssistantIn(BaseModel):
    topic: str = Field(min_length=2, max_length=40)


TOPICS = {
    "budget": "Explain a practical beginner budget and how to separate needs, wants, and savings in India.",
    "credit": "Explain credit card statement balance, minimum due, interest and why paying the total due matters. Do not quote a universal interest rate.",
    "emergency": "Explain how to think about an emergency fund without prescribing a product.",
    "upi": "Explain common UPI social engineering red flags and why a PIN is not required to receive money.",
    "mutual_funds": "Explain NAV, fund risk, fees and why historical returns are not guarantees. Do not recommend individual funds.",
}
_usage = OrderedDict()
_demo_hits = []


@router.post("/assistant/explain")
async def explain(payload: AssistantIn, request: Request, owner: str = Depends(owner_id)):
    # Only curated, nonpersonal prompts can reach a free-tier external model.
    if payload.topic not in TOPICS:
        raise HTTPException(422, "Choose one of the available learning topics.")
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise HTTPException(503, "Pip AI is not connected. Add a Gemini API key to enable general learning explanations.")
    identity = owner if owner != "demo" else (request.client.host if request.client else "local")
    now = time.monotonic()
    if os.getenv('PUBLIC_DEMO')=='true':
        _demo_hits[:] = [t for t in _demo_hits if now-t < 3600]
        if len(_demo_hits)>=20:
            raise HTTPException(429,'The shared Pip demo has reached its hourly limit. Try again later.',headers={'Retry-After':'3600'})
        _demo_hits.append(now)
    hits = [t for t in _usage.get(identity, []) if now - t < 3600]
    if len(hits) >= 10:
        raise HTTPException(429, "Learning limit reached. Please try again in an hour.")
    _usage[identity] = hits + [now]
    _usage.move_to_end(identity)
    while len(_usage) > 1000:
        _usage.popitem(last=False)
    model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", model):
        raise HTTPException(503, "Invalid assistant model configuration.")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await generate(client, f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", headers={"x-goog-api-key": key}, json={
                "systemInstruction": {"parts": [{"text": "You are Pip, a financial literacy educator for India. Use plain English, under 180 words. Do not provide personalized investment advice, guaranteed returns or requests for credentials. End with a brief educational disclaimer."}]},
                "contents": [{"parts": [{"text": TOPICS[payload.topic]}]}],
                "generationConfig": {"maxOutputTokens": 450, "temperature": 0.3}})
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("candidates"), list):
            raise ValueError()
        answer = "\n".join(part.get("text", "") for candidate in body["candidates"][:1] for part in candidate.get("content", {}).get("parts", []) if isinstance(part, dict) and isinstance(part.get("text"), str) and not part.get("thought"))
        if not answer.strip():
            raise ValueError()
        return {"answer": answer, "source": "Gemini", "data_sent": "Selected general learning topic only. No workspace records."}
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code==429:
            raise HTTPException(429,'Pip’s AI provider quota is temporarily exhausted. Please try later.',headers={'Retry-After':'60'})
        raise HTTPException(502,'Pip’s AI provider is unavailable. Please try again later.')
    except (httpx.HTTPError, ValueError, TypeError, AttributeError, KeyError):
        raise HTTPException(502, "The learning provider could not answer. Check its quota, key and model configuration.")
