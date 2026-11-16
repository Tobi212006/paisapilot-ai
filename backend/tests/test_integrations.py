import asyncio
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import owner_id
from app.database import init_db
from app.services import providers


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "records.db"))
    for name in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY", "UPSTOX_ANALYTICS_TOKEN", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    app.dependency_overrides.clear()
    providers._cache.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    providers._cache.clear()


def test_import_preview_atomic_validation_and_duplicates(client):
    text = "description,amount,category,occurred_on,direction\nSample pay,10000,Income,2026-11-01,income\nSample lunch,100,Food,2026-11-02,expense\nSample lunch,100,Food,2026-11-02,expense"
    before = client.get("/api/dashboard").json()
    preview = client.post("/api/transactions/import", json={"csv_text": text}).json()
    assert preview["ready"] == 2 and preview["duplicates_skipped"] == 1
    assert client.get("/api/dashboard").json() == before
    saved = client.post("/api/transactions/import", json={"csv_text": text, "confirm": True}).json()
    assert saved["imported"] == 2
    totals = client.get("/api/dashboard").json()
    assert totals["total_income"] == 10000 and totals["total_spent"] == before["total_spent"] + 100
    repeated = client.post("/api/transactions/import", json={"csv_text": text, "confirm": True}).json()
    assert repeated["imported"] == 0 and repeated["duplicates_skipped"] == 3
    invalid = text + "\nBad date,50,Food,2026-02-31,expense"
    assert client.post("/api/transactions/import", json={"csv_text": invalid, "confirm": True}).status_code == 422
    assert client.get("/api/dashboard").json() == totals


def test_owner_isolation_export_and_deletion(client):
    app.dependency_overrides[owner_id] = lambda: "alice"
    assert client.get("/api/dashboard").json()["transaction_count"] == 0
    client.post("/api/transactions", json={"description": "Alice lunch", "amount": 200, "category": "Food", "occurred_on": "2026-11-15", "owner_id": "bob"})
    client.post("/api/goals", json={"title": "Alice goal", "target_amount": 1000})
    client.post("/api/invoices", json={"customer_label": "Alice customer", "taxable_amount": 100, "gst_rate": 18})
    alice = client.get("/api/records/export").json()
    assert all(len(alice[t]) == 1 for t in ("transactions", "goals", "invoices"))
    app.dependency_overrides[owner_id] = lambda: "bob"
    for path in ("transactions", "goals", "invoices"):
        assert client.get(f"/api/{path}").json() == []
    assert client.get("/api/dashboard").json()["total_spent"] == 0
    assert client.post("/api/records/clear", json={"confirmation": "no"}).status_code == 422
    client.post("/api/records/clear", json={"confirmation": "DELETE MY RECORDS"})
    app.dependency_overrides[owner_id] = lambda: "alice"
    assert client.get("/api/records/export").json() == alice
    client.post("/api/records/clear", json={"confirmation": "DELETE MY RECORDS"})
    assert client.get("/api/records/export").json() == {"transactions": [], "goals": [], "invoices": [], "budgets": [], "goal_movements": []}


def test_private_mode_rejects_missing_token_and_partial_config(client, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    assert client.get("/api/dashboard").status_code == 503
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "public-test-key")
    for path in ("dashboard", "transactions", "goals", "invoices", "records/export"):
        assert client.get(f"/api/{path}").status_code == 401
    assert client.post("/api/transactions/import", json={"csv_text": "x"}).status_code == 401


def test_supabase_validates_token_with_provider(client, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "public-test-key")
    real_async_client = httpx.AsyncClient
    def handle(request):
        assert str(request.url) == "https://example.supabase.co/auth/v1/user"
        if request.headers.get("Authorization") == "Bearer good-token":
            return httpx.Response(200, json={"id": "verified-owner"})
        return httpx.Response(401, json={"message": "Invalid token"})
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: real_async_client(transport=httpx.MockTransport(handle), **kwargs))
    assert client.get("/api/dashboard", headers={"Authorization": "Bearer forged"}).status_code == 401
    result = client.get("/api/dashboard", headers={"Authorization": "Bearer good-token"})
    assert result.status_code == 200 and result.json()["transaction_count"] == 0


def test_provider_status_and_missing_credentials(client):
    status = client.get("/api/connections").json()
    assert status["workspace_mode"] == "demo" and not status["upstox"]["configured"]
    assert client.get("/api/stocks/quote", params={"instrument": "NSE_EQ|INE002A01018"}).status_code == 503
    assert client.post("/api/assistant/explain", json={"topic": "budget"}).status_code == 503
    assert client.post("/api/assistant/explain", json={"topic": "my personal bank statement"}).status_code == 422


def test_provider_normalization_and_validation(client, monkeypatch):
    async def fake_get(url, **kwargs):
        if "frankfurter" in url:
            return [{"date": "2026-11-13", "rate": 84.5}], False, "timestamp"
        if url.endswith("search"):
            return [{"schemeCode": 119551, "schemeName": "Sample fund"}], False, "timestamp"
        return {"meta": {"scheme_name": "Sample fund"}, "data": [{"date": "13-11-2026", "nav": "100.50"}, {"date": "12-11-2026", "nav": "99.25"}]}, True, "timestamp"
    monkeypatch.setattr(providers, "get_json", fake_get)
    rate = client.get("/api/currency?base=USD&quote=INR").json()
    assert rate["rate"] == 84.5 and rate["source"] == "Frankfurter"
    assert client.get("/api/currency?base=INR&quote=INR").json()["rate"] == 1
    assert client.get("/api/currency?base=BAD&quote=INR").status_code == 422
    assert len(client.get("/api/funds/search?q=Sample").json()["results"]) == 1
    fund = client.get("/api/funds/119551").json()
    assert fund["history"][0]["date"] == "2026-11-12" and fund["latest"]["nav"] == 100.5
    assert client.get("/api/funds/1").status_code == 422


def test_provider_cache_and_failure_have_no_demo_fallback(client, monkeypatch):
    real_async_client = httpx.AsyncClient
    calls = []
    def handle(request):
        calls.append(request)
        if "outage" in str(request.url):
            return httpx.Response(503)
        return httpx.Response(200, json=[{"rate": 90}])
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: real_async_client(transport=httpx.MockTransport(handle), **kwargs))
    async def run():
        first = await providers.get_json("https://example.test/rates")
        second = await providers.get_json("https://example.test/rates")
        assert first[1] is False and second[1] is True
        assert len(calls) == 1
        with pytest.raises(Exception) as exc:
            await providers.get_json("https://example.test/outage")
        assert exc.value.status_code == 502
    asyncio.run(run())


def test_delete_does_not_reseed_and_rejects_bad_values(client):
    client.post("/api/records/clear", json={"confirmation": "DELETE MY RECORDS"})
    init_db()
    assert client.get("/api/dashboard").json()["transaction_count"] == 0
    for amount in (-1, 0, "NaN", "Infinity"):
        assert client.post("/api/transactions", json={"description": "Invalid", "amount": amount, "category": "Food", "occurred_on": "2026-11-15"}).status_code == 422


def test_assistant_sends_only_curated_topic_and_enforces_quota(client, monkeypatch):
    from app.routers.connections import _usage
    import json
    _usage.clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    real_async_client = httpx.AsyncClient
    requests = []
    def handle(request):
        requests.append(request)
        assert request.headers["x-goog-api-key"] == "test-secret"
        body = json.loads(request.content)
        assert body["contents"][0]["parts"][0]["text"].startswith("Explain credit card")
        assert "transactions" not in body and "owner_id" not in body
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "Read the full statement balance. Educational only."}]}}]})
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: real_async_client(transport=httpx.MockTransport(handle), **kwargs))
    for _ in range(10):
        response = client.post("/api/assistant/explain", json={"topic": "credit", "transactions": "MUST NOT BE SENT"})
        assert response.status_code == 200
    assert client.post("/api/assistant/explain", json={"topic": "credit"}).status_code == 429
    assert len(requests) == 10
    _usage.clear()


def test_read_only_stock_adapter_keeps_token_on_server(client, monkeypatch):
    monkeypatch.setenv("UPSTOX_ANALYTICS_TOKEN", "private-token")
    real_async_client = httpx.AsyncClient
    def handle(request):
        assert request.url.host == "api.upstox.com"
        assert request.headers["Authorization"] == "Bearer private-token"
        assert request.method == "GET"
        return httpx.Response(200, json={"status": "success", "data": {"NSE_EQ:EXAMPLE": {"last_price": 100}}})
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: real_async_client(transport=httpx.MockTransport(handle), **kwargs))
    response = client.get("/api/stocks/quote", params={"instrument": "NSE_EQ|EXAMPLE"})
    assert response.status_code == 200 and "private-token" not in response.text
    assert response.json()["quotes"]["NSE_EQ:EXAMPLE"]["last_price"] == 100
