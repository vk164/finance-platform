from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from transactions.models.transaction import TransactionKind

Description = Annotated[
    str,
    StringConstraints(max_length=200, strip_whitespace=True)
]
Money = Annotated[Decimal, Field(gt=0, decimal_places=2, max_digits=12)]
CurrencyCode = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]

class TransactionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    amount: Money
    currency_code: CurrencyCode
    kind: TransactionKind
    description: Description | None = None


class TransactionRead(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime