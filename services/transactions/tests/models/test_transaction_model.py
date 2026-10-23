from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid7

import pytest
from transactions.models.transaction import Transaction, TransactionKind


def test_create_transaction() -> None:
    now = datetime.now(UTC)

    transaction = Transaction(
        id=uuid7(),
        amount=Decimal(1500.50),
        currency_code='RUR',
        kind=TransactionKind.EXPENSE,
        description='new laptop',
        created_at=now,
        updated_at=now
    )

    assert transaction.amount == Decimal(1500.50)
    assert transaction.currency_code == 'RUR'
    assert transaction.kind == TransactionKind.EXPENSE
    assert transaction.created_at == now


# noinspection dataclass
def test_transaction_is_immutable() -> None:
    transaction = Transaction(
        id=uuid7(),
        amount=Decimal("100"),
        currency_code='USD',
        kind=TransactionKind.INCOME,
        description="Salary",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with pytest.raises(FrozenInstanceError):
        transaction.amount = Decimal("200") # pyright: ignore[reportAttributeAccessIssue]