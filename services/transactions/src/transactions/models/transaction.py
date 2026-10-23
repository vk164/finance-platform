from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class TransactionKind(StrEnum):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'



@dataclass(frozen=True, slots=True)
class Transaction:
    id: UUID
    amount: Decimal
    currency_code: str
    kind: TransactionKind
    description: str | None
    created_at: datetime
    updated_at: datetime
