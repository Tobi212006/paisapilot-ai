import json
from uuid import uuid4
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import owner_id
from app.database import connect, init_db
from app.routers import planning


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'planning.db'))
    monkeypatch.delenv('GROQ_API_KEY',raising=False)
    app.dependency_overrides[owner_id]=lambda:'alice'
    planning._ai_usage.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def entry(**changes):
    return dict(description='Cafe',amount='100.29',category='Food',occurred_on='2026-10-10',direction='expense',**changes) if not changes else {**entry(),**changes}


def add(client,**changes):
    r=client.post('/api/transactions',json=entry(**changes))
    assert r.status_code==201,r.text
    return r.json()['id']


def test_month_money_types_evidence_and_period(client):
    expense=add(client)
    refund=add(client,description='Refund',amount='0.29',direction='refund')
    add(client,description='Salary',amount='1000',direction='income')
    add(client,description='Own account',amount='900',direction='transfer')
    add(client,description='Prior purchase',amount='50',occurred_on='2026-09-10')
    result=client.get('/api/planning/month?month=2026-10').json()
    assert result['net_spending']==100 and result['recorded_cash_flow']==900
    assert result['transaction_count']==4 and result['transfers_excluded']==1
    assert result['facts'][0]['transaction_ids']==[expense,refund]
    assert result['comparison']['current']==100 and result['comparison']['previous']==50
    assert result['comparison']['percent']==100
    assert result['coverage']['complete'] is False
    assert 'owner_id' not in json.dumps(result)


@pytest.mark.parametrize('month',['2026-13','2026-2','0001-01','2026-00','wrong','2026-10-01'])
def test_invalid_month(client,month):
    assert client.get('/api/planning/month',params={'month':month}).status_code==422


def test_missing_comparison_is_not_zero_and_owner_isolation(client):
    record=add(client)
    assert client.get('/api/planning/month?month=2026-10').json()['comparison'] is None
    app.dependency_overrides[owner_id]=lambda:'bob'
    assert client.get('/api/planning/month?month=2026-10').json()['transaction_count']==0
    assert client.post(f'/api/planning/transactions/{record}',json=entry()).status_code==404


def test_budget_edit_and_removal_and_decimal_validation(client):
    add(client)
    payload={'month':'2026-10','category':'Food','limit':'100'}
    assert client.post('/api/planning/budgets',json=payload).status_code==200
    b=client.get('/api/planning/month?month=2026-10').json()['budgets'][0]
    assert b['spent']==100.29 and b['remaining']==-0.29
    assert client.post('/api/planning/budgets',json={**payload,'limit':'NaN'}).status_code==422
    client.post('/api/planning/budgets',json={**payload,'limit':'0'})
    assert client.get('/api/planning/month?month=2026-10').json()['budgets']==[]


def test_edit_recalculates_and_transfer_excluded(client):
    record=add(client)
    assert client.post(f'/api/planning/transactions/{record}',json=entry(direction='transfer')).status_code==200
    assert client.get('/api/planning/month?month=2026-10').json()['net_spending']==0


def test_goal_contribution_withdrawal_history_and_bounds(client):
    goal=client.post('/api/goals',json={'title':'Emergency fund','target_amount':1000}).json()['id']
    url=f'/api/planning/goals/{goal}/movements'
    assert client.post(url,json={'amount':'250.29'}).json()['saved_amount']==250.29
    assert client.post(url,json={'amount':'-0.29'}).json()['saved_amount']==250
    assert client.post(url,json={'amount':-251}).status_code==422
    assert client.post(url,json={'amount':751}).status_code==422
    assert len(client.get(url).json())==2
    app.dependency_overrides[owner_id]=lambda:'bob'
    assert client.get(url).status_code==404
    assert client.post(url,json={'amount':1}).status_code==404


def test_csv_mapping_separate_credit_debit_and_date_formats(client):
    text='Narration,Txn Date,Withdrawal,Deposit\nCafe,10/10/2026,100.29,\nSalary,11/10/2026,,1000\nBroken,12/10/2026,100,100'
    r=client.post('/api/review/preview',json={'text':text,'date_format':'DD/MM/YYYY'}).json()
    assert r['rows'][0]['values']['amount']=='100.29'
    assert r['rows'][0]['values']['category']=='Food'
    assert r['rows'][1]['values']['direction']=='income'
    assert r['rows'][1]['values']['occurred_on']=='2026-10-11'
    assert r['rows'][2]['issues'] and not r['rows'][2]['include']
    assert client.get('/api/transactions').json()==[]


def test_unmapped_columns_return_mapping_and_malformed_rows_fail(client):
    r=client.post('/api/review/preview',json={'text':'Memo,Day,Value\nLunch,2026-10-01,12'}).json()
    assert r['rows']==[] and r['headers']==['Memo','Day','Value']
    r=client.post('/api/review/preview',json={'text':'Memo,Day,Value\nLunch,2026-10-01,12','mapping':{'description':'Memo','occurred_on':'Day','amount':'Value'}}).json()
    assert r['rows'][0]['values']['amount']=='12'
    assert client.post('/api/review/preview',json={'text':'description,date,amount\nCafe,2026-10-01,12,extra'}).status_code==422
    assert client.post('/api/review/preview',json={'text':'date,date\na,b'}).status_code==422


def test_sms_no_date_assumption_and_no_raw_message_retention(client):
    text='INR 250 debited at Cafe on 2026-10-03. Account XX1234.\nINR 800 credited from Employer'
    r=client.post('/api/review/preview',json={'text':text,'source':'sms'}).json()
    assert r['rows'][0]['values']['description']=='Cafe'
    assert 'XX1234' not in json.dumps(r)
    assert r['rows'][1]['values']['occurred_on']==''
    assert not r['rows'][1]['include']
    assert client.get('/api/transactions').json()==[]


def test_duplicates_are_warnings_commit_requires_ack_and_is_idempotent(client):
    add(client)
    text='description,amount,category,occurred_on,direction\nCafe,100.29,Food,2026-10-10,expense'
    row=client.post('/api/review/preview',json={'text':text}).json()['rows'][0]
    assert row['possible_duplicate_ids'] and not row['include']
    payload={'request_id':str(uuid4()),'rows':[entry()]}
    assert client.post('/api/review/commit',json=payload).status_code==409
    payload['acknowledge_duplicates']=True
    assert client.post('/api/review/commit',json=payload).json()['imported']==1
    assert client.post('/api/review/commit',json=payload).json()['replayed'] is True
    assert len(client.get('/api/transactions').json())==2
    assert client.post('/api/review/commit',json={**payload,'rows':[entry(amount=9)]}).status_code==409


def test_batch_undo_restore_and_owner_isolation(client):
    batch=client.post('/api/review/commit',json={'request_id':str(uuid4()),'rows':[entry()]}).json()['batch_id']
    url=f'/api/review/batches/{batch}'
    assert client.post(url,json={'undone':True}).status_code==200
    assert client.get('/api/planning/month?month=2026-10').json()['transaction_count']==0
    assert client.get('/api/transactions').json()==[]
    assert client.get('/api/records/export').json()['transactions']==[]
    assert client.get('/api/dashboard').json()['transaction_count']==0
    assert client.post(url,json={'undone':False}).status_code==200
    assert client.get('/api/planning/month?month=2026-10').json()['net_spending']==100.29
    app.dependency_overrides[owner_id]=lambda:'bob'
    assert client.get('/api/review/batches').json()==[]
    assert client.post(url,json={'undone':True}).status_code==404


def test_import_validation_atomic_and_export_clear_new_records(client):
    payload={'request_id':str(uuid4()),'rows':[entry(),entry(amount=-1)]}
    assert client.post('/api/review/commit',json=payload).status_code==422
    assert client.get('/api/transactions').json()==[]
    client.post('/api/planning/budgets',json={'month':'2026-10','category':'Food','limit':100})
    assert client.get('/api/records/export').json()['budgets']
    client.post('/api/records/clear',json={'confirmation':'DELETE MY RECORDS'})
    assert client.get('/api/records/export').json()['budgets']==[]


def test_ai_consent_missing_provider_and_no_fabricated_fallback(client):
    add(client)
    assert client.post('/api/planning/explain',json={'month':'2026-10'}).status_code==422
    response=client.post('/api/planning/explain',json={'month':'2026-10','consent':True})
    assert response.status_code==503 and 'no data was sent' in response.json()['detail']


@pytest.mark.parametrize('provider_status,expected',[(429,429),(401,503),(404,503),(500,502)])
def test_ai_provider_failures_have_actionable_status(client,monkeypatch,provider_status,expected):
    add(client)
    monkeypatch.setenv('GEMINI_API_KEY','test-key')
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(lambda request:httpx.Response(provider_status,json={})),**kwargs))
    response=client.post('/api/planning/explain',json={'month':'2026-10','consent':True})
    assert response.status_code==expected
    assert 'test-key' not in response.text
    if provider_status==429:assert response.headers['retry-after']=='60'


def test_provider_status_is_configuration_only(client,monkeypatch):
    assert client.get('/api/planning/provider').json()['configured'] is False
    monkeypatch.setenv('GEMINI_API_KEY','test-key')
    r=client.get('/api/planning/provider').json()
    assert r['provider']=='Google Gemini' and r['verified'] is False
    assert 'test-key' not in json.dumps(r)


@pytest.mark.parametrize('explanation,status',[('These are incomplete recorded totals. Review the underlying entries before changing your plan.',200),('You will save 900 next month.',502)])
def test_ai_aggregate_only_output_validation_and_quota(client,monkeypatch,explanation,status):
    add(client,description='Secret merchant name',category='Private custom label')
    monkeypatch.setenv('GROQ_API_KEY','test-not-a-real-key')
    original=httpx.AsyncClient
    def handler(request):
        body=request.content.decode()
        assert 'Secret merchant' not in body and 'Private custom' not in body
        assert '2026-10-10' not in body
        return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'explanation':explanation})}}]})
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    response=client.post('/api/planning/explain',json={'month':'2026-10','consent':True})
    assert response.status_code==status
    planning._ai_usage['alice']=[planning.time.monotonic()]*10
    assert client.post('/api/planning/explain',json={'month':'2026-10','consent':True}).status_code==429


def test_migration_idempotent_and_legacy_money_preserved(client):
    add(client)
    init_db();init_db()
    with connect() as db:
        assert db.execute("SELECT value FROM app_meta WHERE key='schema_version'").fetchone()['value']=='3'
        assert db.execute("SELECT amount_paise FROM transactions WHERE owner_id='alice'").fetchone()['amount_paise']==10029


@pytest.mark.parametrize('text,expected',[('Never share your OTP with anyone.',False),("Do not enter your PIN to receive money.",False),('Please share OTP to receive a refund',True),('Never share OTP. But tell your password to claim a prize',True)])
def test_safety_negation_and_real_request(client,text,expected):
    result=client.post('/api/safety/check',json={'description':text}).json()
    assert any('Sensitive credential' in rule for rule in result['rules_triggered']) is expected
