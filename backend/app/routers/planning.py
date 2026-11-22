"""Evidence-backed monthly planning. Calculations never depend on an LLM."""
import calendar
import json
import os
import re
import time
from collections import OrderedDict
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field
import httpx
from ..services.gemini import generate
from ..auth import owner_id
from ..database import connect
from ..money import paise, rupees
from ..schemas import FinanceModel, TransactionIn

router = APIRouter(prefix='/api/planning')
_ai_usage = OrderedDict()


@router.get('/provider')
def explanation_provider():
    if os.getenv('PUBLIC_DEMO')=='true':
        return {'provider':None,'configured':False,'verified':False,'notice':'Financial-summary AI is disabled in the shared demo. Pip learning topics may be available.'}
    provider = 'Groq' if os.getenv('GROQ_API_KEY') else 'Google Gemini' if os.getenv('GEMINI_API_KEY') else None
    return {'provider': provider, 'configured': bool(provider), 'verified': False, 'notice': 'Configured is not a live health check. Explanations require explicit sharing consent.'}


def month_range(month):
    if not re.fullmatch(r'\d{4}-\d{2}', month):
        raise HTTPException(422, 'Choose a YYYY-MM month.')
    try:
        first = date.fromisoformat(month + '-01')
        if first.year < 1900:
            raise ValueError()
        end = date(first.year, first.month, calendar.monthrange(first.year, first.month)[1])
    except ValueError:
        raise HTTPException(422, 'Choose a valid month.')
    return first, end


def month_snapshot(month, owner):
    first, end = month_range(month)
    previous_end = first.fromordinal(first.toordinal() - 1)
    previous_start = previous_end.replace(day=1)
    # Compare the same elapsed number of calendar days for the current partial month.
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    current_partial = first <= today < end
    comparison_end = min(today, end) if current_partial else end
    previous_cutoff = previous_end.replace(day=min(comparison_end.day, previous_end.day))
    with connect() as db:
        rows = [dict(r) for r in db.execute('SELECT id,description,amount_paise,category,occurred_on,direction FROM transactions WHERE owner_id=? AND archived_at IS NULL AND occurred_on BETWEEN ? AND ? ORDER BY occurred_on,id', (owner, first.isoformat(), end.isoformat()))]
        prior = [dict(r) for r in db.execute('SELECT id,amount_paise,category,occurred_on,direction FROM transactions WHERE owner_id=? AND archived_at IS NULL AND occurred_on BETWEEN ? AND ?', (owner, previous_start.isoformat(), previous_cutoff.isoformat()))]
        budgets = [dict(r) for r in db.execute('SELECT category,limit_paise FROM budgets WHERE owner_id=? AND month=? ORDER BY category', (owner, month))]
    income = sum(r['amount_paise'] for r in rows if r['direction'] == 'income')
    gross = sum(r['amount_paise'] for r in rows if r['direction'] == 'expense')
    refunds = sum(r['amount_paise'] for r in rows if r['direction'] == 'refund')
    categories = {}
    for r in rows:
        if r['direction'] in ('expense', 'refund'):
            c = categories.setdefault(r['category'], {'amount': 0, 'ids': []})
            c['amount'] += r['amount_paise'] * (-1 if r['direction'] == 'refund' else 1)
            c['ids'].append(r['id'])
    facts = []
    for index, (category, values) in enumerate(sorted(categories.items(), key=lambda x: -x[1]['amount'])):
        facts.append({'id': f'category-{index}', 'title': f'{category}: recorded net spending', 'value': rupees(values['amount']), 'calculation': 'Sum of recorded expenses minus recorded refunds in this category.', 'transaction_ids': values['ids'], 'limitation': 'Only imported or entered records are included. Refunds are counted in the month received.'})
    for b in budgets:
        spent = categories.get(b['category'], {}).get('amount', 0)
        b.update(limit=rupees(b.pop('limit_paise')), spent=rupees(spent))
        b['remaining'] = round(b['limit'] - b['spent'], 2)
        b['percent'] = round(b['spent'] / b['limit'] * 100, 1)
    elapsed = [r for r in rows if r['occurred_on'] <= comparison_end.isoformat()]
    spend = lambda records: sum(r['amount_paise'] * (-1 if r['direction'] == 'refund' else 1) for r in records if r['direction'] in ('expense', 'refund'))
    comparison = None
    if prior and elapsed:
        previous = spend(prior)
        current = spend(elapsed)
        comparison = {'current': rupees(current), 'previous': rupees(previous), 'change': rupees(current - previous), 'percent': round((current-previous)/previous*100, 1) if previous > 0 else None, 'current_end': comparison_end.isoformat(), 'previous_start': previous_start.isoformat(), 'previous_end': previous_cutoff.isoformat(), 'transaction_ids': [r['id'] for r in elapsed if r['direction'] in ('expense', 'refund')], 'previous_transaction_ids': [r['id'] for r in prior if r['direction'] in ('expense', 'refund')], 'limitation': 'Calendar periods may have different lengths. Missing imports can make comparisons misleading.'}
    return {'month': month, 'income': rupees(income), 'gross_expenses': rupees(gross), 'refunds': rupees(refunds), 'net_spending': rupees(gross-refunds), 'recorded_cash_flow': rupees(income-gross+refunds), 'transaction_count': len(rows), 'transfers_excluded': sum(r['direction']=='transfer' for r in rows), 'coverage': {'first': min((r['occurred_on'] for r in rows), default=None), 'last': max((r['occurred_on'] for r in rows), default=None), 'complete': False, 'note': 'Coverage shows dates of recorded entries, not proof of a complete bank statement.'}, 'partial_month': current_partial, 'comparison': comparison, 'budgets': budgets, 'facts': facts, 'transactions': [{**{k:v for k,v in r.items() if k!='amount_paise'}, 'amount': rupees(r['amount_paise'])} for r in rows], 'mode': 'sample' if owner=='demo' else 'private', 'explanation_mode': 'Calculated evidence; no external AI request made.'}


@router.get('/month')
def monthly(month: str = Query(...), owner: str = Depends(owner_id)):
    return month_snapshot(month, owner)


class BudgetIn(FinanceModel):
    month: str
    category: str = Field(min_length=2, max_length=40)
    limit: Decimal = Field(ge=0, le=100_000_000, decimal_places=2)


@router.post('/budgets')
def save_budget(payload: BudgetIn, owner: str = Depends(owner_id)):
    month_range(payload.month)
    with connect() as db:
        if payload.limit == 0:
            db.execute('DELETE FROM budgets WHERE owner_id=? AND month=? AND category=?', (owner,payload.month,payload.category))
        else:
            db.execute('INSERT INTO budgets(owner_id,month,category,limit_paise) VALUES(?,?,?,?) ON CONFLICT(owner_id,month,category) DO UPDATE SET limit_paise=excluded.limit_paise', (owner,payload.month,payload.category,paise(payload.limit)))
    return {'saved': True}


@router.post('/transactions/{record_id}')
def edit_transaction(record_id: int, payload: TransactionIn, owner: str = Depends(owner_id)):
    with connect() as db:
        result = db.execute('UPDATE transactions SET description=?,amount=?,amount_paise=?,category=?,occurred_on=?,direction=? WHERE id=? AND owner_id=? AND archived_at IS NULL', (payload.description,float(payload.amount),paise(payload.amount),payload.category,payload.occurred_on.isoformat(),payload.direction,record_id,owner))
        if result.rowcount != 1:
            raise HTTPException(404, 'Transaction not found.')
    return {'saved': True}


class MovementIn(FinanceModel):
    amount: Decimal = Field(ge=-100_000_000, le=100_000_000, decimal_places=2)
    note: str = Field(default='Manual adjustment', min_length=2, max_length=100)


@router.post('/goals/{goal_id}/movements')
def move_goal(goal_id: int, payload: MovementIn, owner: str = Depends(owner_id)):
    amount = paise(payload.amount)
    if amount == 0:
        raise HTTPException(422, 'Enter a nonzero contribution or withdrawal.')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        goal = db.execute('SELECT * FROM goals WHERE id=? AND owner_id=?', (goal_id, owner)).fetchone()
        if not goal:
            raise HTTPException(404, 'Goal not found.')
        saved = goal['saved_paise'] + amount
        if not 0 <= saved <= goal['target_paise']:
            raise HTTPException(422, 'The new saved amount must be between zero and the goal target.')
        db.execute('UPDATE goals SET saved_paise=?,saved_amount=? WHERE id=? AND owner_id=?', (saved,rupees(saved),goal_id,owner))
        db.execute('INSERT INTO goal_movements(goal_id,owner_id,amount_paise,note) VALUES(?,?,?,?)', (goal_id,owner,amount,payload.note))
    return {'saved_amount': rupees(saved), 'notice': 'Tracking update only; no money has moved between bank accounts.'}


@router.get('/goals/{goal_id}/movements')
def goal_history(goal_id: int, owner: str = Depends(owner_id)):
    with connect() as db:
        if not db.execute('SELECT id FROM goals WHERE id=? AND owner_id=?',(goal_id,owner)).fetchone():
            raise HTTPException(404,'Goal not found.')
        return [{'amount':rupees(r['amount_paise']),'note':r['note'],'created_at':r['created_at']} for r in db.execute('SELECT * FROM goal_movements WHERE goal_id=? AND owner_id=? ORDER BY id DESC',(goal_id,owner))]


class ExplainIn(FinanceModel):
    month: str
    consent: bool = False


@router.post('/explain')
async def explain_month(payload: ExplainIn, owner: str = Depends(owner_id)):
    if os.getenv('PUBLIC_DEMO')=='true':
        raise HTTPException(403,'Financial-summary sharing is disabled in the public demo. Use Pip in Learn for general topics.')
    if not payload.consent:
        raise HTTPException(422, 'Confirm sharing the displayed monthly totals before requesting external AI.')
    snapshot = month_snapshot(payload.month, owner)
    # Only these numeric aggregate fields leave the server. No raw statements,
    # merchant/category labels, transaction text, identities, or goal names.
    facts = {key: snapshot[key] for key in ('income','gross_expenses','refunds','net_spending','recorded_cash_flow','transaction_count')}
    key = os.getenv('GROQ_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not key:
        raise HTTPException(503, 'AI is not connected. Calculated evidence remains available; no data was sent.')
    if not snapshot['transaction_count']:
        raise HTTPException(422, 'Add records for this month first.')
    now = time.monotonic()
    hits = [t for t in _ai_usage.get(owner, []) if now-t < 3600]
    if len(hits) >= 10:
        raise HTTPException(429, 'AI explanation limit reached. Try again in an hour.')
    _ai_usage[owner] = hits + [now]
    _ai_usage.move_to_end(owner)
    while len(_ai_usage)>1000:
        _ai_usage.popitem(last=False)
    prompt = 'Explain these user-entered monthly totals in plain English. They are incomplete records, not verified bank balances. Do not invent causes, merchants, trends or transactions. No investment advice. Use no numbers or currency symbols in your explanation; the UI displays exact calculations separately. Return ONLY JSON with one field explanation, maximum 600 characters. Data: '+json.dumps(facts)
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=False) as client:
            if os.getenv('GROQ_API_KEY'):
                provider='Groq'
                response=await client.post('https://api.groq.com/openai/v1/chat/completions',headers={'Authorization':'Bearer '+key},json={'model':os.getenv('GROQ_MODEL','openai/gpt-oss-20b'),'messages':[{'role':'user','content':prompt}],'response_format':{'type':'json_object'},'max_completion_tokens':350})
                response.raise_for_status()
                content=response.json()['choices'][0]['message']['content']
            else:
                provider='Gemini'
                model=os.getenv('GEMINI_MODEL','gemini-3.1-flash-lite')
                if not re.fullmatch(r'[a-zA-Z0-9_.-]+',model):
                    raise ValueError()
                response=await generate(client, f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseMimeType':'application/json','maxOutputTokens':350}})
                response.raise_for_status()
                content=response.json()['candidates'][0]['content']['parts'][0]['text']
        explanation=json.loads(content)['explanation']
        if not isinstance(explanation,str) or not 10<=len(explanation)<=600 or re.search(r'[\d₹$€£<>]',explanation):
            raise ValueError()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(429,'The AI provider quota is currently exhausted. Try later; calculated evidence is still available.',headers={'Retry-After':'60'})
        if exc.response.status_code in (401,403,404):
            raise HTTPException(503,'The AI provider rejected its key or model configuration. Calculated evidence is still available.')
        raise HTTPException(502,'The AI provider is unavailable. Calculated evidence is still available.')
    except (httpx.HTTPError,ValueError,KeyError,IndexError,TypeError):
        raise HTTPException(502,'AI could not return a usable explanation. Your calculated evidence is unchanged.')
    return {'provider':provider,'explanation':explanation,'facts_sent':facts,'limitations':'AI-generated wording can be wrong. Verify it against the calculated evidence. No raw transaction text was shared.'}
