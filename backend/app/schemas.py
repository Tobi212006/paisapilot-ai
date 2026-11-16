import re
from datetime import date
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class FinanceModel(BaseModel):
    model_config = {"allow_inf_nan": False}

    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, value):
        return value.strip() if isinstance(value, str) else value


def calendar_date(value):
    if value is None or type(value) is date:
        return value
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Use a YYYY-MM-DD calendar date.")
    return date.fromisoformat(value)


class TransactionIn(FinanceModel):
    description: str = Field(min_length=2, max_length=120)
    amount: Decimal = Field(gt=0, le=10_000_000, decimal_places=2)
    category: str = Field(min_length=2, max_length=40)
    occurred_on: date
    direction: Literal["expense", "income", "transfer", "refund"] = "expense"
    _date = field_validator("occurred_on", mode="before")(calendar_date)


class SafetyIn(FinanceModel):
    description: str = Field(min_length=2, max_length=1000)
    amount: Decimal = Field(default=Decimal(0), ge=0, le=10_000_000, decimal_places=2)


class MarketIn(FinanceModel):
    prices: list[float] = Field(min_length=2, max_length=5000)
    sma_period: int = Field(default=5, ge=2, le=500)


class GSTIn(FinanceModel):
    taxable_amount: Decimal = Field(ge=0, le=100_000_000, decimal_places=2)
    gst_rate: Decimal = Field(ge=0, le=100, decimal_places=4)
    intra_state: bool = True


class InvoiceIn(GSTIn):
    customer_label: str = Field(min_length=2, max_length=100)


class GoalIn(FinanceModel):
    title: str = Field(min_length=2, max_length=100)
    target_amount: Decimal = Field(gt=0, le=100_000_000, decimal_places=2)
    saved_amount: Decimal = Field(default=Decimal(0), ge=0, le=100_000_000, decimal_places=2)
    target_date: Optional[date] = None
    _date = field_validator("target_date", mode="before")(calendar_date)

    @model_validator(mode="after")
    def savings_within_target(self):
        if self.saved_amount > self.target_amount:
            raise ValueError("Saved amount cannot exceed target amount.")
        return self
