import re
import math

def safety_screen(description: str, amount: float):
    text = description.lower()
    rules = []
    clauses = re.split(r'[.!?;\n]|\bbut\b', text)
    requesting = any(re.search(r'\b(pin|otp|password)\b', clause) and re.search(r'\b(share|tell|send|provide|enter)\b', clause) and not re.search(r"\b(never|do not|don't|dont|avoid)\s+(?:ever\s+)?(?:share|tell|send|provide|enter)\b", clause) for clause in clauses)
    if requesting:
        rules.append("Sensitive credential requested: never share a UPI PIN, OTP or password.")
    if re.search(r"\b(refund|cashback|prize|kyc)\b", text) and re.search(r"\b(link|click|urgent|verify)\b", text):
        rules.append("Urgent link or verification language combined with a financial claim.")
    if amount >= 100000:
        rules.append("High-value amount: independently verify recipient and purpose.")
    score = min(100, len(rules) * 35)
    band = "high" if score >= 70 else "review" if score >= 35 else "low-signal"
    return {"risk_score": score, "risk_band": band, "rules_triggered": rules,
            "method": "Local language rules; no AI or payment verification.",
            "disclaimer": "Heuristic educational screening only; not a definitive fraud finding. No warning does not mean a message or payment is safe."}

def indicators(prices: list[float], period: int):
    if len(prices) < 2 or not isinstance(period, int) or period < 2:
        raise ValueError("At least two prices and a period of two or more are required.")
    if any(not math.isfinite(p) or p <= 0 or p > 1e12 for p in prices):
        raise ValueError("Prices must be finite, positive, and at most one trillion.")
    sma = sum(prices[-period:]) / period if len(prices) >= period else None
    changes = [b-a for a,b in zip(prices, prices[1:])][-14:]
    gains = [max(x,0) for x in changes]
    losses = [max(-x,0) for x in changes]
    avg_gain = sum(gains)/len(changes)
    avg_loss = sum(losses)/len(changes)
    rsi = 100.0 if avg_loss == 0 and avg_gain > 0 else 50.0 if avg_loss == 0 else 100-(100/(1+avg_gain/avg_loss))
    return {"sma": sma, "sma_period": period, "rsi_14_approx": round(rsi,2),
            "data_mode": "user-supplied historical prices; not live market data"}
