import asyncio
import httpx
import pytest
from app.services.gemini import generate


@pytest.mark.parametrize('status,attempts', [(200,1),(400,1),(401,1),(403,1),(404,1),(429,1),(503,2)])
def test_provider_status_retry_policy(status, attempts):
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result=await generate(client,'https://example.test/generate',headers={'x-goog-api-key':'synthetic-key'},json={'contents':[]})
            assert result.status_code==status
    asyncio.run(run())
    assert len(calls)==attempts


def test_transient_transport_failure_recovers_once():
    calls=[]
    def handler(request):
        calls.append(request)
        if len(calls)==1:
            raise httpx.ReadTimeout('synthetic failure')
        return httpx.Response(200,json={'answer':'educational'})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            assert (await generate(client,'https://example.test/generate',headers={},json={})).status_code==200
    asyncio.run(run())
    assert len(calls)==2


def test_transport_failure_stops_after_two_attempts():
    calls=[]
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout('synthetic failure')
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(httpx.ReadTimeout):
                await generate(client,'https://example.test/generate',headers={},json={})
    asyncio.run(run())
    assert len(calls)==2
