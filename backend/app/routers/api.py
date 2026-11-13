from fastapi import APIRouter, HTTPException
from ..database import connect
from ..schemas import TransactionIn, SafetyIn, MarketIn, GSTIn, InvoiceIn, GoalIn
from ..services.analytics import safety_screen, indicators

router = APIRouter(prefix="/api")

@router.get("/dashboard")
def dashboard():
    with connect() as db:
        rows = db.execute("SELECT category, SUM(amount) total FROM transactions GROUP BY category").fetchall()
        total = db.execute("SELECT COALESCE(SUM(amount),0) total FROM transactions").fetchone()["total"]
        count = db.execute("SELECT COUNT(*) n FROM transactions").fetchone()["n"]
    return {"total_spent": total, "transaction_count": count, "by_category": [dict(r) for r in rows], "currency": "INR", "data_label": "demo/local records"}

@router.get("/transactions")
def transactions():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM transactions ORDER BY occurred_on DESC, id DESC").fetchall()]

@router.post("/transactions", status_code=201)
def add_transaction(payload: TransactionIn):
    with connect() as db:
        cur = db.execute("INSERT INTO transactions(description,amount,category,occurred_on) VALUES(?,?,?,?)",
                         (payload.description, payload.amount, payload.category, payload.occurred_on))
        return dict(db.execute("SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)).fetchone())

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
    tax = round(payload.taxable_amount * payload.gst_rate / 100, 2)
    return {"taxable_amount": payload.taxable_amount, "gst_rate": payload.gst_rate,
            "cgst": round(tax/2,2) if payload.intra_state else 0,
            "sgst": round(tax/2,2) if payload.intra_state else 0,
            "igst": 0 if payload.intra_state else tax,
            "total": round(payload.taxable_amount+tax,2),
            "disclaimer": "Illustrative estimate; verify current applicable GST treatment."}

@router.post("/invoices", status_code=201)
def create_invoice(payload: InvoiceIn):
    tax = round(payload.taxable_amount*payload.gst_rate/100,2)
    total = round(payload.taxable_amount+tax,2)
    with connect() as db:
        cur = db.execute("INSERT INTO invoices(customer_label,taxable_amount,gst_rate,total_amount) VALUES(?,?,?,?)",
                         (payload.customer_label,payload.taxable_amount,payload.gst_rate,total))
        return dict(db.execute("SELECT * FROM invoices WHERE id=?",(cur.lastrowid,)).fetchone())

@router.get("/invoices")
def invoices():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()]

@router.get("/goals")
def goals():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM goals ORDER BY id DESC").fetchall()]

@router.post("/goals", status_code=201)
def create_goal(payload: GoalIn):
    if payload.saved_amount > payload.target_amount:
        raise HTTPException(422, "Saved amount cannot exceed target amount.")
    with connect() as db:
        cur = db.execute("INSERT INTO goals(title,target_amount,saved_amount,target_date) VALUES(?,?,?,?)",
                         (payload.title,payload.target_amount,payload.saved_amount,payload.target_date))
        return dict(db.execute("SELECT * FROM goals WHERE id=?",(cur.lastrowid,)).fetchone())
