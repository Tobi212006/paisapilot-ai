import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError
from ..auth import owner_id
from ..database import connect
from ..schemas import TransactionIn
from ..money import paise

router = APIRouter(prefix="/api")


class CSVIn(BaseModel):
    csv_text: str = Field(min_length=1, max_length=250000)
    confirm: bool = False


def parse_csv(text):
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    required = {"description", "amount", "category", "occurred_on"}
    if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)) or not required.issubset(set(reader.fieldnames)) or set(reader.fieldnames)-required-{"direction"}:
        raise HTTPException(422, "CSV needs description,amount,category,occurred_on columns; optional direction is income or expense.")
    parsed = []
    try:
        raw_rows = list(reader)
    except csv.Error:
        raise HTTPException(422, "Malformed CSV. Check quotes and separators.")
    for line, row in enumerate(raw_rows, start=2):
        if len(parsed) >= 500:
            raise HTTPException(422, "Import at most 500 rows at a time.")
        try:
            if None in row or any(v is None for v in row.values()):
                raise ValueError()
            values = {k: (row.get(k) or "").strip() for k in required}
            values["direction"] = (row.get("direction") or "expense").strip().lower()
            item = TransactionIn(**values)
            if not item.description.strip() or not item.category.strip():
                raise ValueError()
            parsed.append(item)
        except (ValidationError, ValueError, TypeError):
            raise HTTPException(422, f"Invalid transaction on CSV line {line}. Use positive amounts and YYYY-MM-DD dates.")
    if not parsed:
        raise HTTPException(422, "CSV has no transaction rows.")
    return parsed


@router.post("/transactions/import")
def import_transactions(payload: CSVIn, owner: str = Depends(owner_id)):
    parsed = parse_csv(payload.csv_text)
    accepted, seen, duplicates = [], set(), 0
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        for item in parsed:
            key = (item.description.strip(), float(item.amount), item.category.strip(), item.occurred_on.isoformat(), item.direction)
            exists = db.execute("SELECT id FROM transactions WHERE description=? AND amount_paise=? AND category=? AND occurred_on=? AND direction=? AND archived_at IS NULL AND owner_id=?", (key[0], paise(item.amount), *key[2:], owner)).fetchone()
            if key in seen or exists:
                duplicates += 1
                continue
            seen.add(key)
            accepted.append(item)
            if payload.confirm:
                db.execute("INSERT INTO transactions(description,amount,category,occurred_on,direction,owner_id,amount_paise) VALUES(?,?,?,?,?,?,?)", (*key, owner, paise(item.amount)))
    return {"imported": len(accepted) if payload.confirm else 0, "ready": len(accepted), "duplicates_skipped": duplicates, "preview": [{**item.model_dump(mode="json"), "amount": float(item.amount)} for item in accepted[:10]], "confirmed": payload.confirm}


@router.get("/records/export")
def export_records(owner: str = Depends(owner_id)):
    with connect() as db:
        return {"transactions": [dict(r) for r in db.execute("SELECT id,description,amount,category,occurred_on,direction FROM transactions WHERE archived_at IS NULL AND owner_id=?", (owner,))], "goals": [dict(r) for r in db.execute("SELECT id,title,target_amount,saved_amount,target_date FROM goals WHERE owner_id=?", (owner,))], "budgets": [dict(r) for r in db.execute("SELECT month,category,limit_paise FROM budgets WHERE owner_id=?", (owner,))], "goal_movements": [dict(r) for r in db.execute("SELECT goal_id,amount_paise,note,created_at FROM goal_movements WHERE owner_id=?", (owner,))], "invoices": [dict(r) for r in db.execute("SELECT id,customer_label,taxable_amount,gst_rate,total_amount,status FROM invoices WHERE owner_id=?", (owner,))]}


class ClearIn(BaseModel):
    confirmation: str


@router.post("/records/clear")
def clear_records(payload: ClearIn, owner: str = Depends(owner_id)):
    if payload.confirmation != "DELETE MY RECORDS":
        raise HTTPException(422, "Type DELETE MY RECORDS to confirm.")
    with connect() as db:
        for table in ("goal_movements", "transactions", "goals", "invoices", "budgets", "import_batches"):
            db.execute(f"DELETE FROM {table} WHERE owner_id=?", (owner,))
    return {"deleted": True, "scope": "workspace records only; sign-in account is retained"}
