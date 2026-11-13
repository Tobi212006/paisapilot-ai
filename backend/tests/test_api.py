from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

def test_api(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    init_db()
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/api/dashboard").json()["currency"] == "INR"
        tx = client.post("/api/transactions", json={"description":"Test meal","amount":100,"category":"Food","occurred_on":"2026-11-13"})
        assert tx.status_code == 201
        safety = client.post("/api/safety/check", json={"description":"share OTP to receive refund link","amount":500}).json()
        assert safety["risk_band"] == "high"
        market = client.post("/api/market/indicators", json={"prices":[10,11,12,13,14],"sma_period":3})
        assert market.status_code == 200 and market.json()["sma"] == 13
        gst = client.post("/api/business/gst-estimate", json={"taxable_amount":1000,"gst_rate":18,"intra_state":True}).json()
        assert gst["total"] == 1180
