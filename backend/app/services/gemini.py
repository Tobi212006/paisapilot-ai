"""Bounded retries for read-only Gemini explanations; never log provider payloads."""
import asyncio
import httpx


async def generate(client, url, *, headers, json):
    """At most two attempts within 25 seconds; quota and bad requests are final."""
    try:
        async with asyncio.timeout(25):
            for attempt in range(2):
                try:
                    response = await client.post(url, headers=headers, json=json, timeout=12)
                except httpx.TransportError:
                    if attempt:
                        raise
                else:
                    if response.status_code < 500 or attempt:
                        return response
                await asyncio.sleep(0.3)
    except TimeoutError:
        raise httpx.TimeoutException("AI provider deadline exceeded") from None
