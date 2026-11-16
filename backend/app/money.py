"""All persisted money and aggregation use integer paise, never float sums."""
from decimal import Decimal, ROUND_HALF_UP


def paise(amount):
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def rupees(amount_paise):
    return float(Decimal(amount_paise or 0) / 100)


def gst_values(taxable_amount, gst_rate, intra_state=True):
    base = paise(taxable_amount)
    tax = int((Decimal(base) * Decimal(str(gst_rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    cgst = tax // 2 if intra_state else 0
    sgst = tax - cgst if intra_state else 0
    return {"taxable_amount": rupees(base), "gst_rate": float(gst_rate), "cgst": rupees(cgst), "sgst": rupees(sgst), "igst": 0 if intra_state else rupees(tax), "total": rupees(base + tax), "disclaimer": "Illustrative estimate; rounding remainder is allocated to SGST. Verify applicable GST treatment."}
