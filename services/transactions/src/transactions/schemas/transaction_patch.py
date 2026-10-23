from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from transactions.models.transaction import TransactionKind
from transactions.schemas.transaction import CurrencyCode, Description, Money


class TransactionPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: Money | None = None
    currency_code: CurrencyCode | None = None
    kind: TransactionKind | None = None
    description: Description | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field is required")

        for field_name in self.model_fields_set:
            if field_name == "description":
                continue
            if getattr(self, field_name) is None:
                raise ValueError(
                    f"{field_name} cannot be null"
                )

        return self
