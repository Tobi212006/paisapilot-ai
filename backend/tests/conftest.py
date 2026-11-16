import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    # Tests must never use developer keys or connect to their private workspace.
    for key in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "UPSTOX_ANALYTICS_TOKEN", "PUBLIC_DEMO", "DEMO_LEARNING_AI"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEMO_MODE", "true")
    from app.main import app
    app.middleware_stack = None
    from app.routers.connections import _demo_hits
    _demo_hits.clear()
