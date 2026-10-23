import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid7

import pytest
from transactions.models.transaction import Transaction, TransactionKind
from transactions.schemas.transaction import TransactionRead


@pytest.fixture
def domain_transaction() -> Transaction:
    now = datetime.now(UTC)

    return Transaction(
        id=uuid7(),
        amount=Decimal("1500.50"),
        currency_code='EUR',
        kind=TransactionKind.EXPENSE,
        description="New laptop",
        created_at=now,
        updated_at=now,
    )


def test_convert_domain_model_to_schema(
    domain_transaction: Transaction,
) -> None:
    result = TransactionRead.model_validate(domain_transaction)

    assert result.id == domain_transaction.id
    assert result.amount == domain_transaction.amount
    assert result.currency_code == domain_transaction.currency_code
    assert result.kind == domain_transaction.kind
    assert result.description == domain_transaction.description
    assert result.created_at == domain_transaction.created_at
    assert result.updated_at == domain_transaction.updated_at


def test_model_dump(
    domain_transaction: Transaction,
) -> None:
    schema = TransactionRead.model_validate(domain_transaction)

    data = schema.model_dump()

    assert isinstance(data, dict)
    assert isinstance(data["amount"], Decimal)
    assert data["id"] == domain_transaction.id


def test_json_serialization(
    domain_transaction: Transaction,
) -> None:
    schema = TransactionRead.model_validate(domain_transaction)

    data = json.loads(schema.model_dump_json())

    assert data["id"] == str(domain_transaction.id)
    assert data["amount"] == "1500.50"
    assert data["currency_code"] == "EUR"
    assert data["kind"] == "expense"
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)
