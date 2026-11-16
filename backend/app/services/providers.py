"""Fixed-host public-data adapters. No user financial records leave the database."""
import asyncio
import os
import math
import hashlib
import time
from collections import OrderedDict
from datetime import datetime, timezone
import httpx
from fastapi import HTTPException

_cache: OrderedDict = OrderedDict()
_lock = asyncio.Lock()


async def get_json(url, *, params=None, headers=None, ttl=900):
    # Separate provider credentials without retaining raw bearer tokens as cache keys.
    scope = hashlib.sha256((headers or {}).get("Authorization", "").encode()).hexdigest()
    key = (url, tuple(sorted((params or {}).items())), scope)
    async with _lock:
        cached = _cache.get(key)
        if cached and cached[0] > time.monotonic():
            _cache.move_to_end(key)
            return cached[1], True, cached[2]
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            response = await client.get(url, params=params, headers=headers)
        if response.status_code == 429:
            raise HTTPException(503, "The data provider is busy. Please try again shortly.")
        response.raise_for_status()
        if len(response.content) > 4_000_000:
            raise ValueError("Oversized provider response")
        data = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "The financial data provider is unavailable. No sample values have been substituted.")
    fetched = datetime.now(timezone.utc).isoformat()
    async with _lock:
        _cache[key] = (time.monotonic() + ttl, data, fetched)
        _cache.move_to_end(key)
        while len(_cache) > 128:
            _cache.popitem(last=False)
    return data, False, fetched


async def fund_search(query):
    data, cached, fetched = await get_json("https://api.mfapi.in/mf/search", params={"q": query}, ttl=3600)
    if not isinstance(data, list):
        raise HTTPException(502, "Unexpected fund-provider response.")
    results = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            code, name = int(item["schemeCode"]), item["schemeName"]
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        if 10000 <= code <= 99999999 and isinstance(name, str) and name.strip():
            results.append({"schemeCode": code, "schemeName": name.strip()[:300]})
        if len(results) == 20:
            break
    if data and not results:
        raise HTTPException(502, "The fund provider returned malformed search results.")
    return {"results": results, "source": "MFapi.in", "cached": cached, "fetched_at": fetched}


async def fund_history(code):
    data, cached, fetched = await get_json(f"https://api.mfapi.in/mf/{code}", ttl=3600)
    if not isinstance(data, dict) or not data.get("data"):
        raise HTTPException(404, "No published NAV history found for this scheme.")
    if not isinstance(data["data"], list) or not isinstance(data.get("meta"), dict):
        raise HTTPException(502, "Unexpected fund-history response.")
    points = []
    for item in data["data"]:
        try:
            nav = float(item["nav"])
            if math.isfinite(nav) and nav > 0:
                points.append({"date": datetime.strptime(item["date"], "%d-%m-%Y").date().isoformat(), "nav": nav})
        except (KeyError, ValueError, TypeError):
            continue
    points.sort(key=lambda p: p["date"])
    if not points:
        raise HTTPException(502, "The fund provider returned no usable NAV values.")
    meta = {field: str(data["meta"].get(field, "Not supplied"))[:300] for field in ("scheme_name", "fund_house", "scheme_category")}
    return {"meta": meta, "history": points[-365:], "latest": points[-1], "source": "MFapi.in", "cached": cached, "fetched_at": fetched, "data_mode": "Published mutual fund NAV; not live trading prices."}


async def exchange_rates(base, quote):
    if base == quote:
        return {"base": base, "quote": quote, "rate": 1, "date": None, "source": "Identity conversion", "cached": False, "fetched_at": None}
    data, cached, fetched = await get_json("https://api.frankfurter.dev/v2/rates", params={"base": base, "quotes": quote}, ttl=3600)
    if not isinstance(data, list) or not data:
        raise HTTPException(404, "No reference rate is available for this currency pair.")
    try:
        rate = float(data[0]["rate"])
        date = datetime.strptime(data[0]["date"], "%Y-%m-%d").date().isoformat()
        if not math.isfinite(rate) or rate <= 0:
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        raise HTTPException(502, "Unexpected exchange-rate response.")
    return {"base": base, "quote": quote, "rate": rate, "date": date, "source": "Frankfurter", "cached": cached, "fetched_at": fetched, "data_mode": "Published reference rate; your bank may use a different rate and fees."}


async def stock_quote(instrument):
    token = os.getenv("UPSTOX_ANALYTICS_TOKEN", "")
    if not token:
        raise HTTPException(503, "Upstox is not connected. Add a read-only Analytics Token to the backend environment.")
    data, cached, fetched = await get_json("https://api.upstox.com/v2/market-quote/ltp", params={"instrument_key": instrument}, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, ttl=60)
    if not isinstance(data, dict) or data.get("status") != "success" or not isinstance(data.get("data"), dict) or not data["data"]:
        raise HTTPException(502, "No market quote returned. Check the instrument and provider access.")
    quotes = {}
    for name, value in data["data"].items():
        try:
            price = float(value["last_price"])
        except (ValueError, TypeError, KeyError, OverflowError):
            continue
        if math.isfinite(price) and price >= 0:
            quotes[str(name)[:100]] = {"last_price": price, "instrument_token": str(value.get("instrument_token", ""))[:100]}
    if not quotes:
        raise HTTPException(502, "The stock provider returned no valid prices.")
    return {"quotes": quotes, "source": "Upstox", "cached": cached, "fetched_at": fetched, "data_mode": "Read-only provider snapshot. Check exchange time; not a trade recommendation."}
