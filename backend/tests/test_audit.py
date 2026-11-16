import sqlite3
from decimal import Decimal
import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.auth import owner_id
from app.database import init_db, connect
from app.config import validate_configuration
from app.money import paise, gst_values
from app.security import RequestGuards
from app.services import providers
from app.services.analytics import indicators, safety_screen


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path/'audit.db'))
    app.dependency_overrides.clear()
    providers._cache.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.parametrize('amount',[-1,0,'NaN','Infinity','0.001','10000000.01'])
def test_transaction_amount_contract(client,amount):
    r=client.post('/api/transactions',json={'description':'Audit','amount':amount,'category':'Food','occurred_on':'2026-11-15'})
    assert r.status_code==422
    assert 'input' not in r.json()['errors'][0]


@pytest.mark.parametrize('day',['2026-02-30','not-a-date','2026-1-1',0,'2026-01-01T10:00:00'])
def test_calendar_dates(client,day):
    assert client.post('/api/transactions',json={'description':'Audit','amount':1,'category':'Food','occurred_on':day}).status_code==422


@pytest.mark.parametrize('route,payload',[
 ('goals',{'title':'  ','target_amount':100}),('goals',{'title':'Goal','target_amount':100,'saved_amount':101}),
 ('goals',{'title':'Goal','target_amount':100,'target_date':'2026-02-31'}),
 ('business/gst-estimate',{'taxable_amount':100,'gst_rate':101}),('invoices',{'customer_label':'  ','taxable_amount':100,'gst_rate':18}),
 ('safety/check',{'description':'  '}),('market/indicators',{'prices':[1]}),('market/indicators',{'prices':[0,1]}),
 ('market/indicators',{'prices':[1,2],'sma_period':1}),('market/indicators',{'prices':[1,'Infinity']})])
def test_each_write_validates(client,route,payload):
    assert client.post('/api/'+route,json=payload).status_code==422


def test_exact_money_totals_and_odd_cent_tax(client):
    app.dependency_overrides[owner_id]=lambda:'audit-user'
    for amount in ['0.10','0.20']:
        assert client.post('/api/transactions',json={'description':'Small amount','amount':amount,'category':'Food','occurred_on':'2026-11-15'}).status_code==201
    assert client.get('/api/dashboard').json()['total_spent']==0.3
    with connect() as db:
        assert [r['amount_paise'] for r in db.execute("SELECT amount_paise FROM transactions WHERE owner_id='audit-user' ORDER BY id")]==[10,20]
    r=client.post('/api/business/gst-estimate',json={'taxable_amount':'0.05','gst_rate':18}).json()
    assert Decimal(str(r['cgst']))+Decimal(str(r['sgst']))==Decimal('0.01')
    assert r['total']==0.06
    assert client.post('/api/invoices',json={'customer_label':'Client','taxable_amount':'0.05','gst_rate':18}).json()['total_amount']==0.06
    assert client.post('/api/goals',json={'title':'Tiny target','target_amount':'0.30','saved_amount':'0.10','target_date':'2027-01-01'}).status_code==201
    exported=client.get('/api/records/export').json()
    assert exported['goals'][0]['saved_amount']==0.1


def test_no_nonfinite_input_echo(client):
    r=client.post('/api/transactions',content='{"description":"Secret","amount":NaN,"category":"Food","occurred_on":"2026-11-15"}',headers={'Content-Type':'application/json'})
    assert r.status_code==422 and 'Secret' not in r.text and 'NaN' not in r.text


@pytest.mark.parametrize('text',[
 'description,amount,category,occurred_on,amount\nx,1,Food,2026-11-15,1',
 'description,amount,category,occurred_on,extra\nx,1,Food,2026-11-15,x',
 'description,amount,category,occurred_on\nx,1,Food',
 'description,amount,category,occurred_on\nx,1,Food,2026-11-15,unexpected',
 'description,amount,category,occurred_on\n"unclosed,1,Food,2026-11-15',
 'description,amount,category,occurred_on\n',
 'not,a,template\n1,2,3',
 'description,amount,category,occurred_on\n'+('Lunch,1,Food,2026-11-15\n'*501)])
def test_csv_edge_cases_are_atomic(client,text):
    before=client.get('/api/dashboard').json()
    assert client.post('/api/transactions/import',json={'csv_text':text,'confirm':True}).status_code==422
    assert client.get('/api/dashboard').json()==before


def test_cors_security_headers_and_readiness(client):
    response=client.get('/api/dashboard')
    assert response.headers['X-Content-Type-Options']=='nosniff'
    assert response.headers['Cache-Control']=='no-store' and response.headers['X-Request-ID']
    assert client.get('/ready').json()['status']=='ready'
    allowed=client.options('/api/dashboard',headers={'Origin':'http://localhost:5174','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'Authorization'})
    assert allowed.status_code==200
    denied=client.options('/api/dashboard',headers={'Origin':'https://evil.example','Access-Control-Request-Method':'GET'})
    assert 'Access-Control-Allow-Origin' not in denied.headers


def test_body_size_and_content_type_guards(client):
    assert client.post('/api/transactions/import',json={'csv_text':'x'*300001}).status_code==413
    assert client.post('/api/safety/check',content='text').status_code==415


def test_rate_limit_and_sanitized_internal_errors():
    small=FastAPI()
    small.add_middleware(RequestGuards,limit=2)
    @small.get('/api/ping')
    def ping():return {'ok':True}
    @small.get('/broken')
    def broken():raise RuntimeError('PRIVATE INTERNAL DETAILS')
    with TestClient(small) as c:
        assert c.get('/api/ping').status_code==200
        assert c.get('/api/ping').status_code==200
        assert c.get('/api/ping').status_code==429
        response=c.get('/broken')
        assert response.status_code==500 and 'PRIVATE INTERNAL DETAILS' not in response.text


def test_production_configuration_fails_closed(monkeypatch):
    monkeypatch.setenv('APP_ENV','production')
    with pytest.raises(RuntimeError):validate_configuration()
    monkeypatch.setenv('SUPABASE_URL','https://project.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','public-key')
    monkeypatch.setenv('DEMO_MODE','false')
    monkeypatch.setenv('DATABASE_PATH','production.db')
    monkeypatch.setenv('CORS_ORIGINS','https://app.example.com')
    validate_configuration()
    monkeypatch.setenv('CORS_ORIGINS','*')
    with pytest.raises(RuntimeError):validate_configuration()


@pytest.mark.parametrize('url,key',[('http://remote.example','key'),('https://user:pass@example.com','key'),('https://project.supabase.co/path','key'),('https://project.supabase.co','sb_secret_bad')])
def test_rejects_bad_account_configuration(monkeypatch,url,key):
    monkeypatch.setenv('SUPABASE_URL',url);monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY',key)
    with pytest.raises(RuntimeError):validate_configuration()


def test_auth_provider_malformed_or_unavailable(client,monkeypatch):
    monkeypatch.setenv('SUPABASE_URL','https://project.supabase.co');monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','public-key')
    real=httpx.AsyncClient
    for body in [[],{}, {'id':42}]:
        monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:real(transport=httpx.MockTransport(lambda req:httpx.Response(200,json=body)),**kwargs))
        assert client.get('/api/dashboard',headers={'Authorization':'Bearer token'}).status_code==503


@pytest.mark.parametrize('kind,data',[
 ('funds/search?q=Fund',{}),('funds/search?q=Fund',[None,{'schemeCode':None}]),
 ('funds/122639',{'meta':[],'data':[1]}),('funds/122639',{'meta':{},'data':[{'date':'bad','nav':'NaN'}]}),
 ('currency?base=USD&quote=INR',[{'rate':-1,'date':'2026-11-15'}]),('currency?base=USD&quote=INR',[None]),
 ('stocks/quote?instrument=NSE_EQ%7CEXAMPLE',[]),('stocks/quote?instrument=NSE_EQ%7CEXAMPLE',{'status':'success','data':{'bad':{'last_price':'NaN'}}})])
def test_malformed_provider_data_never_becomes_a_500(client,monkeypatch,kind,data):
    monkeypatch.setenv('UPSTOX_ANALYTICS_TOKEN','test-token')
    async def fake(*args,**kwargs):return data,False,'timestamp'
    monkeypatch.setattr(providers,'get_json',fake)
    assert client.get('/api/'+kind).status_code==502


@pytest.mark.parametrize('prices,period,expected', [([1,2,3],2,(2.5,100)),([3,2,1],2,(1.5,0)),([2,2,2],5,(None,50))])
def test_market_math(prices,period,expected):
    r=indicators(prices,period);assert (r['sma'],r['rsi_14_approx'])==expected


@pytest.mark.parametrize('prices,period',[([],2),([1],2),([1,2],1),([1,float('nan')],2),([1,-1],2),([1,1e20],2)])
def test_market_service_rejects_invalid_inputs(prices,period):
    with pytest.raises(ValueError):indicators(prices,period)


def test_safety_rules_are_explainable():
    assert safety_screen('Please share OTP for refund link',100000)['risk_score']==100
    assert safety_screen('Lunch with friends',100)['risk_band']=='low-signal'
    assert paise('0.10')==10
    assert gst_values(100,18,False)['igst']==18


def test_integer_money_migrates_existing_database(tmp_path,monkeypatch):
    path=tmp_path/'legacy.db';monkeypatch.setenv('DATABASE_PATH',str(path))
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE transactions(id INTEGER PRIMARY KEY,description TEXT,amount REAL,category TEXT,occurred_on TEXT,created_at TEXT)')
        db.execute("INSERT INTO transactions VALUES(1,'Legacy',0.29,'Food','2026-11-15','now')")
    init_db();init_db()
    with connect() as db:
        row=db.execute('SELECT * FROM transactions WHERE id=1').fetchone()
        assert row['amount_paise']==29 and row['owner_id']=='demo'


def test_backup_preserves_data_and_refuses_overwrite(tmp_path):
    from scripts.backup_database import backup_database
    source=tmp_path/'source.db';dest=tmp_path/'backup.db'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE records (value TEXT)');db.execute("INSERT INTO records VALUES('sample')")
    backup_database(source,dest)
    with sqlite3.connect(dest) as db:
        assert db.execute('SELECT value FROM records').fetchone()[0]=='sample'
    with pytest.raises(ValueError):backup_database(source,dest)
    with pytest.raises(ValueError):backup_database(tmp_path/'absent.db',tmp_path/'new.db')


def test_readiness_reports_database_failure(client,tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path))
    assert client.get('/ready').status_code==503


def test_production_headers_and_no_demo_auth_fallback(client,monkeypatch):
    monkeypatch.setenv('APP_ENV','production');monkeypatch.setenv('DEMO_MODE','false')
    response=client.get('/api/dashboard')
    assert response.status_code==503
    assert "frame-ancestors 'none'" in response.headers['content-security-policy']
    assert response.headers['strict-transport-security']=='max-age=31536000'
