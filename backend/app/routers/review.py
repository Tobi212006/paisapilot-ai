"""Local import extraction with editable review; no imported text is sent to AI."""
import csv
import hashlib
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, ValidationError
from ..auth import owner_id
from ..database import connect
from ..schemas import FinanceModel, TransactionIn
from ..money import paise

router = APIRouter(prefix='/api/review')
ALIASES = {'description':['description','narration','particulars','merchant','payee'], 'occurred_on':['occurredon','date','transactiondate','txndate'], 'amount':['amount','transactionamount'], 'debit':['debit','withdrawal','debitamount','withdrawalamount'], 'credit':['credit','deposit','creditamount','depositamount'], 'category':['category'], 'direction':['direction','type']}


def suggest_category(description, direction):
    if direction=='income':
        return 'Income', 'Suggested from the income transaction type; review before saving.'
    for category, words in [('Food',r'grocer|cafe|restaurant|swiggy|zomato'),('Transport',r'uber|ola\b|metro|bus\b|petrol|fuel'),('Bills',r'electric|recharge|broadband|internet|utility'),('Housing',r'\brent\b'),('Education',r'tuition|course|school|college'),('Health',r'pharmacy|hospital|clinic|medicine')]:
        if re.search(words,description,re.I):
            return category, 'Local keyword suggestion; not an AI or verified merchant classification.'
    return 'Uncategorized', 'No reliable local category match. Please choose a category.'


def money_text(text):
    value=re.sub(r'(?i)\b(?:INR|Rs\.?)\s*|₹|,','',str(text)).strip()
    return str(Decimal(value))


def duplicate_ids(db, item, owner):
    return [r['id'] for r in db.execute('SELECT id FROM transactions WHERE owner_id=? AND archived_at IS NULL AND description=? AND amount_paise=? AND occurred_on=? AND direction=?',(owner,item.description,paise(item.amount),item.occurred_on.isoformat(),item.direction))]


def preview_row(values, line, db, owner, issues=None):
    issues=list(issues or [])
    category,reason=suggest_category(values.get('description',''),values.get('direction','expense'))
    if values.get('category'):
        reason='Category supplied by the file; review before saving.'
    values['category']=values.get('category') or category
    matches=[]
    try:
        item=TransactionIn(**values)
        matches=duplicate_ids(db,item,owner)
        values=item.model_dump(mode='json')
    except ValidationError as exc:
        issues.extend('Check '+str(e['loc'][0]).replace('_',' ') for e in exc.errors())
    return {'line':line,'values':values,'issues':list(dict.fromkeys(issues)), 'category_reason':reason,'possible_duplicate_ids':matches,'include':not issues and not matches}


class PreviewIn(FinanceModel):
    text: str = Field(min_length=1,max_length=250000)
    source: Literal['csv','sms'] = 'csv'
    mapping: dict[str,str] = Field(default_factory=dict, max_length=8)
    date_format: Literal['YYYY-MM-DD','DD/MM/YYYY','MM/DD/YYYY'] = 'YYYY-MM-DD'


@router.post('/preview')
def preview(payload: PreviewIn, owner: str = Depends(owner_id)):
    rows=[]
    with connect() as db:
        if payload.source=='sms':
            lines=[line.strip() for line in payload.text.splitlines() if line.strip()]
            if len(lines)>50:
                raise HTTPException(422,'Paste at most 50 messages, one per line.')
            for n,text in enumerate(lines,1):
                amounts=re.findall(r'(?i)(?:\bINR\b|\bRs\.?|₹)\s*([\d,]+(?:\.\d{1,2})?)(?![\d.])',text)
                dates=re.findall(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b',text)
                income=bool(re.search(r'\bcredited\b|\breceived\b',text,re.I))
                expense=bool(re.search(r'\bdebited\b|\bpaid\b|\bspent\b',text,re.I))
                issues=[]
                if len(amounts)!=1:issues.append('Amount is ambiguous or missing; enter the transaction amount.')
                if income==expense:issues.append('Choose whether money came in or went out.')
                when=''
                if len(dates)==1:
                    try:when=datetime.strptime(dates[0],'%Y-%m-%d' if '-' in dates[0] else '%d/%m/%Y').date().isoformat()
                    except ValueError:pass
                if not when:issues.append('Enter the actual transaction date; no date was assumed.')
                # Never persist the full SMS. Extract only a short payee fragment,
                # redact identifiers, and require the user to review it.
                merchant=re.search(r'(?i)\b(?:to|at|from)\s+([A-Za-z][A-Za-z &.-]{1,45}?)(?=\s+(?:on|via|ref|avl|balance)\b|[.;]|$)',text)
                description=merchant.group(1).strip() if merchant else 'Imported transaction'
                values={'description':description[:120], 'amount':money_text(amounts[0]) if len(amounts)==1 else '', 'category':'', 'occurred_on':when,'direction':'income' if income and not expense else 'expense'}
                rows.append(preview_row(values,n,db,owner,issues))
            return {'rows':rows,'headers':[], 'mapping':{},'notice':'Local pattern extraction only. Full messages are not stored or sent to AI. Review every field.'}
        reader=csv.DictReader(io.StringIO(payload.text.lstrip('\ufeff')),strict=True)
        headers=reader.fieldnames
        if not headers or len(headers)!=len(set(headers)) or len(headers)>40:
            raise HTTPException(422,'Use a CSV with unique column headers (at most 40 columns).')
        mapping={}
        for field,aliases in ALIASES.items():
            match=next((h for h in headers if re.sub(r'[^a-z]','',h.lower()) in aliases),None)
            if match:mapping[field]=match
        for field,header in payload.mapping.items():
            if field not in ALIASES or (header and header not in headers):
                raise HTTPException(422,'Choose mapping columns from this CSV.')
            if header:mapping[field]=header
            else:mapping.pop(field,None)
        if not all(k in mapping for k in ('description','occurred_on')) or not ('amount' in mapping or 'debit' in mapping or 'credit' in mapping):
            return {'rows':[],'headers':headers,'mapping':mapping,'notice':'Map description, date, and either amount or debit/credit columns, then preview again.'}
        try:
            raw=list(reader)
        except csv.Error:
            raise HTTPException(422,'Malformed CSV. Check quoted values and separators.')
        if not 1<=len(raw)<=500:
            raise HTTPException(422,'Import between 1 and 500 rows.')
        for line,row in enumerate(raw,2):
            if None in row or any(v is None for v in row.values()):
                raise HTTPException(422,f'CSV line {line} has extra or missing columns.')
            values={field:row[header].strip() for field,header in mapping.items()}
            issues=[]
            direction=values.get('direction','expense').lower()
            direction={'dr':'expense','debit':'expense','cr':'income','credit':'income'}.get(direction,direction)
            try:
                if 'amount' in values:
                    amount=Decimal(money_text(values['amount']))
                    if amount<0:
                        amount=-amount
                        if 'direction' not in mapping:direction='expense'
                        issues.append('Negative amount converted to positive; confirm its transaction type.')
                else:
                    debit=Decimal(money_text(values.get('debit') or '0'))
                    credit=Decimal(money_text(values.get('credit') or '0'))
                    if debit<0 or credit<0 or bool(debit)==bool(credit):raise ValueError()
                    amount=debit or credit
                    direction='expense' if debit else 'income'
                values['amount']=str(amount)
            except (InvalidOperation,ValueError):
                values['amount']=''
                issues.append('Enter one positive amount; debit and credit cannot both be populated.')
            try:values['occurred_on']=datetime.strptime(values['occurred_on'],{'YYYY-MM-DD':'%Y-%m-%d','DD/MM/YYYY':'%d/%m/%Y','MM/DD/YYYY':'%m/%d/%Y'}[payload.date_format]).date().isoformat()
            except ValueError:
                values['occurred_on']=''
                issues.append('Date does not match the selected format.')
            values={k:v for k,v in values.items() if k not in ('debit','credit')}
            values['direction']=direction
            rows.append(preview_row(values,line,db,owner,issues))
    seen=set()
    for row in rows:
        v=row['values'];key=(v.get('description'),v.get('amount'),v.get('occurred_on'),v.get('direction'))
        if key in seen:
            row['issues'].append('Possible duplicate within this file. Include only if it is a separate transaction.')
            row['include']=False
        seen.add(key)
    return {'rows':rows,'headers':headers,'mapping':mapping,'notice':'Local extraction and keyword suggestions. Nothing is saved until confirmation; duplicate warnings are advisory.'}


class CommitIn(FinanceModel):
    request_id: str = Field(min_length=36,max_length=36)
    rows: list[TransactionIn] = Field(min_length=1,max_length=500)
    acknowledge_duplicates: bool = False


@router.post('/commit')
def commit(payload: CommitIn, owner: str = Depends(owner_id)):
    try:UUID(payload.request_id)
    except ValueError:raise HTTPException(422,'Invalid import request identifier.')
    fingerprint=hashlib.sha256(payload.model_dump_json(exclude={'request_id'}).encode()).hexdigest()
    batch=payload.request_id
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        existing=db.execute('SELECT * FROM import_batches WHERE id=?',(batch,)).fetchone()
        if existing:
            if existing['owner_id']!=owner or existing['label']!=fingerprint:
                raise HTTPException(409,'Import identifier already used. Preview again.')
            return {'batch_id':batch,'imported':db.execute('SELECT COUNT(*) n FROM transactions WHERE owner_id=? AND batch_id=? AND archived_at IS NULL',(owner,batch)).fetchone()['n'],'replayed':True}
        seen=set()
        for item in payload.rows:
            key=(item.description,paise(item.amount),item.occurred_on.isoformat(),item.direction)
            if (key in seen or duplicate_ids(db,item,owner)) and not payload.acknowledge_duplicates:
                raise HTTPException(409,'Possible duplicates found. Review them and explicitly allow duplicates if they are legitimate.')
            seen.add(key)
        db.execute('INSERT INTO import_batches(id,owner_id,label) VALUES(?,?,?)',(batch,owner,fingerprint))
        for item in payload.rows:
            db.execute('INSERT INTO transactions(description,amount,category,occurred_on,direction,owner_id,amount_paise,batch_id) VALUES(?,?,?,?,?,?,?,?)',(item.description,float(item.amount),item.category,item.occurred_on.isoformat(),item.direction,owner,paise(item.amount),batch))
    return {'batch_id':batch,'imported':len(payload.rows),'replayed':False}


@router.get('/batches')
def batches(owner: str = Depends(owner_id)):
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT b.id,b.created_at,b.undone,COUNT(t.id) records FROM import_batches b LEFT JOIN transactions t ON t.batch_id=b.id AND t.owner_id=b.owner_id WHERE b.owner_id=? GROUP BY b.id ORDER BY b.created_at DESC LIMIT 20',(owner,))]


class BatchIn(FinanceModel):
    undone: bool


@router.post('/batches/{batch_id}')
def undo_batch(batch_id: str,payload: BatchIn,owner: str = Depends(owner_id)):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT id FROM import_batches WHERE id=? AND owner_id=?',(batch_id,owner)).fetchone():
            raise HTTPException(404,'Import not found.')
        db.execute('UPDATE transactions SET archived_at=? WHERE batch_id=? AND owner_id=?',('import undone' if payload.undone else None,batch_id,owner))
        db.execute('UPDATE import_batches SET undone=? WHERE id=? AND owner_id=?',(payload.undone,batch_id,owner))
    return {'undone':payload.undone,'notice':'Records retained for restore; excluded from totals while undone.'}
