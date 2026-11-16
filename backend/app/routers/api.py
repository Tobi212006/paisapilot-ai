from fastapi import APIRouter, HTTPException, Depends
from ..database import connect
from ..money import paise, rupees, gst_values
from ..auth import owner_id
from ..schemas import TransactionIn, SafetyIn, MarketIn, GSTIn, InvoiceIn, GoalIn
from ..services.analytics import safety_screen, indicators

router = APIRouter(prefix="/api")

def public_record(row):
    return {key: value for key, value in dict(row).items() if key != "owner_id" and not key.endswith("_paise")}


@router.get("/dashboard")
def dashboard(owner: str = Depends(owner_id)):
    with connect() as db:
        rows = db.execute("SELECT category, SUM(CASE WHEN direction='refund' THEN -amount_paise ELSE amount_paise END) total FROM transactions WHERE archived_at IS NULL AND owner_id=? AND direction IN ('expense','refund') GROUP BY category", (owner,)).fetchall()
        total = db.execute("SELECT COALESCE(SUM(CASE WHEN direction='refund' THEN -amount_paise ELSE amount_paise END),0) total FROM transactions WHERE archived_at IS NULL AND owner_id=? AND direction IN ('expense','refund')", (owner,)).fetchone()["total"]
        count = db.execute("SELECT COUNT(*) n FROM transactions WHERE archived_at IS NULL AND owner_id=?", (owner,)).fetchone()["n"]
        income = db.execute("SELECT COALESCE(SUM(amount_paise),0) total FROM transactions WHERE archived_at IS NULL AND owner_id=? AND direction='income'", (owner,)).fetchone()["total"]
    return {"total_income": rupees(income), "net": rupees(income-total), "total_spent": rupees(total), "transaction_count": count, "by_category": [{"category": r["category"], "total": rupees(r["total"])} for r in rows], "currency": "INR", "data_label": "shared local demo records" if owner == "demo" else "your private records"}

@router.get("/transactions")
def transactions(owner: str = Depends(owner_id)):
    with connect() as db:
        return [public_record(r) for r in db.execute("SELECT * FROM transactions WHERE archived_at IS NULL AND owner_id=? ORDER BY occurred_on DESC, id DESC LIMIT 1000", (owner,)).fetchall()]

@router.post("/transactions", status_code=201)
def add_transaction(payload: TransactionIn, owner: str = Depends(owner_id)):
    with connect() as db:
        cur = db.execute("INSERT INTO transactions(description,amount,category,occurred_on,direction,owner_id,amount_paise) VALUES(?,?,?,?,?,?,?)",
                         (payload.description, float(payload.amount), payload.category, payload.occurred_on.isoformat(), payload.direction, owner, paise(payload.amount)))
        return public_record(db.execute("SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)).fetchone())

@router.post("/safety/check")
def check_safety(payload: SafetyIn):
    return safety_screen(payload.description, payload.amount)

@router.post("/market/indicators")
def market_indicators(payload: MarketIn):
    try:
        return indicators(payload.prices, payload.sma_period)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@router.post("/business/gst-estimate")
def gst_estimate(payload: GSTIn):
    return gst_values(payload.taxable_amount, payload.gst_rate, payload.intra_state)

@router.post("/invoices", status_code=201)
def create_invoice(payload: InvoiceIn, owner: str = Depends(owner_id)):
    total = gst_values(payload.taxable_amount, payload.gst_rate, payload.intra_state)["total"]
    with connect() as db:
        cur = db.execute("INSERT INTO invoices(customer_label,taxable_amount,gst_rate,total_amount,owner_id,taxable_paise,total_paise) VALUES(?,?,?,?,?,?,?)",
                         (payload.customer_label,float(payload.taxable_amount),float(payload.gst_rate),total,owner,paise(payload.taxable_amount),paise(total)))
        return public_record(db.execute("SELECT * FROM invoices WHERE id=?",(cur.lastrowid,)).fetchone())

@router.get("/invoices")
def invoices(owner: str = Depends(owner_id)):
    with connect() as db:
        return [public_record(r) for r in db.execute("SELECT * FROM invoices WHERE owner_id=? ORDER BY id DESC", (owner,)).fetchall()]

@router.get("/goals")
def goals(owner: str = Depends(owner_id)):
    with connect() as db:
        return [public_record(r) for r in db.execute("SELECT * FROM goals WHERE owner_id=? ORDER BY id DESC", (owner,)).fetchall()]

@router.post("/goals", status_code=201)
def create_goal(payload: GoalIn, owner: str = Depends(owner_id)):
    if payload.saved_amount > payload.target_amount:
        raise HTTPException(422, "Saved amount cannot exceed target amount.")
    with connect() as db:
        cur = db.execute("INSERT INTO goals(title,target_amount,saved_amount,target_date,owner_id,target_paise,saved_paise) VALUES(?,?,?,?,?,?,?)",
                         (payload.title,float(payload.target_amount),float(payload.saved_amount),payload.target_date.isoformat() if payload.target_date else None,owner,paise(payload.target_amount),paise(payload.saved_amount)))
        return public_record(db.execute("SELECT * FROM goals WHERE id=?",(cur.lastrowid,)).fetchone())
