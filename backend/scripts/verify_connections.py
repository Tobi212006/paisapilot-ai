"""Run from backend: .venv/Scripts/python scripts/verify_connections.py.
Prints statuses only. Never prints keys, tokens, account data or AI output.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services import providers
from app.routers.connections import explain, AssistantIn
from app.config import validate_configuration
from starlette.requests import Request
from dotenv import dotenv_values, load_dotenv
import httpx

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


async def main():
    results = {}
    try:
        validate_configuration()
        results['configuration'] = 'valid'
    except RuntimeError as error:
        results['configuration'] = str(error)
    checks = [('mutual_funds', lambda: providers.fund_history(122639)), ('currency', lambda: providers.exchange_rates('USD','INR'))]
    if os.getenv('UPSTOX_ANALYTICS_TOKEN'):
        checks.append(('upstox', lambda: providers.stock_quote('NSE_EQ|INE002A01018')))
    else:
        results['upstox'] = 'blocked: token missing'
    if os.getenv('GEMINI_API_KEY'):
        checks.append(('gemini', lambda: explain(AssistantIn(topic='budget'), Request({'type':'http','method':'POST','path':'/','headers':[],'client':('127.0.0.1',0)}), owner='configuration-check')))
    else:
        results['gemini'] = 'blocked: key missing'
    for name, check in checks:
        try:
            await check()
            results[name] = 'verified live response'
        except Exception as error:
            results[name] = f'failed: {getattr(error,"status_code","provider or network error")}'
    url, key = os.getenv('SUPABASE_URL','').rstrip('/'), os.getenv('SUPABASE_PUBLISHABLE_KEY','')
    if url and key:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url+'/auth/v1/settings',headers={'apikey':key})
            results['supabase'] = 'settings endpoint reachable; real user sign-in still requires acceptance test' if response.status_code==200 else f'failed: HTTP {response.status_code}'
        except Exception:
            results['supabase'] = 'failed: provider or network error'
    else:
        results['supabase'] = 'blocked: project settings missing'
    front = dotenv_values(Path(__file__).resolve().parents[2]/'frontend'/'.env.local')
    results['frontend_project_match'] = bool(url and key and front.get('VITE_SUPABASE_URL','').rstrip('/')==url and front.get('VITE_SUPABASE_PUBLISHABLE_KEY')==key)
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    asyncio.run(main())
