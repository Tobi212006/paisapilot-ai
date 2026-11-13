from pydantic import BaseModel, Field
from typing import Optional

class TransactionIn(BaseModel):
    description: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0, le=10_000_000)
    category: str = Field(min_length=2, max_length=40)
    occurred_on: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

class SafetyIn(BaseModel):
    description: str = Field(min_length=2, max_length=1000)
    amount: float = Field(default=0, ge=0, le=10_000_000)

class MarketIn(BaseModel):
    prices: list[float] = Field(min_length=2, max_length=5000)
    sma_period: int = Field(default=5, ge=2, le=500)

class GSTIn(BaseModel):
    taxable_amount: float = Field(ge=0, le=100_000_000)
    gst_rate: float = Field(ge=0, le=100)
    intra_state: bool = True

class InvoiceIn(GSTIn):
    customer_label: str = Field(min_length=2, max_length=100)

class GoalIn(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    target_amount: float = Field(gt=0, le=100_000_000)
    saved_amount: float = Field(default=0, ge=0)
    target_date: Optional[str] = None
