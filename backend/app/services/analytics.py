import re

def safety_screen(description: str, amount: float):
    text = description.lower()
    rules = []
    if re.search(r"\b(pin|otp|password)\b", text) and re.search(r"\b(share|tell|send|provide|enter)\b", text):
        rules.append("Sensitive credential requested: never share a UPI PIN, OTP or password.")
    if re.search(r"\b(refund|cashback|prize|kyc)\b", text) and re.search(r"\b(link|click|urgent|verify)\b", text):
        rules.append("Urgent link or verification language combined with a financial claim.")
    if amount >= 100000:
        rules.append("High-value amount: independently verify recipient and purpose.")
    score = min(100, len(rules) * 35)
    band = "high" if score >= 70 else "review" if score >= 35 else "low-signal"
    return {"risk_score": score, "risk_band": band, "rules_triggered": rules,
            "disclaimer": "Heuristic educational screening only; not a definitive fraud finding."}

def indicators(prices: list[float], period: int):
    if any(p <= 0 for p in prices):
        raise ValueError("Prices must be positive.")
    sma = sum(prices[-period:]) / period if len(prices) >= period else None
    changes = [b-a for a,b in zip(prices, prices[1:])][-14:]
    gains = [max(x,0) for x in changes]
    losses = [max(-x,0) for x in changes]
    avg_gain = sum(gains)/len(changes)
    avg_loss = sum(losses)/len(changes)
    rsi = 100.0 if avg_loss == 0 and avg_gain > 0 else 50.0 if avg_loss == 0 else 100-(100/(1+avg_gain/avg_loss))
    return {"sma": sma, "sma_period": period, "rsi_14_approx": round(rsi,2),
            "data_mode": "user-supplied historical prices; not live market data"}
