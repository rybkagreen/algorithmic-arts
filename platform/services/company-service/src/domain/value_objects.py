from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class INN:
    value: str

    def to_dict(self) -> dict:
        return {"value": self.value}


@dataclass(frozen=True)
class OGRN:
    value: str

    def to_dict(self) -> dict:
        return {"value": self.value}


@dataclass(frozen=True)
class FundingAmount:
    amount: float
    currency: str = "USD"

    def to_dict(self) -> dict:
        return {"amount": self.amount, "currency": self.currency}