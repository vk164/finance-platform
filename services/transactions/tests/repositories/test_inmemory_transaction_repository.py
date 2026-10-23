from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid7

import pytest
from transactions.models.transaction import Transaction, TransactionKind
from transactions.repositories.transaction import InMemoryTransactionRepository


@pytest.fixture
def repository() -> InMemoryTransactionRepository:
    return InMemoryTransactionRepository()


@pytest.fixture
def transaction() -> Transaction:
    now = datetime.now(UTC)

    return Transaction(
        id=uuid7(),
        amount=Decimal("1500.50"),
        currency_code="EUR",
        kind=TransactionKind.EXPENSE,
        description="New laptop",
        created_at=now,
        updated_at=now,
    )


def test_add_and_get(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    repository.add(transaction)

    result = repository.get(transaction.id)

    assert result == transaction


def test_get_nonexistent_transaction(
    repository: InMemoryTransactionRepository,
) -> None:
    assert repository.get(uuid7()) is None


def test_list_transactions(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    second = replace(transaction, id=uuid7())

    repository.add(transaction)
    repository.add(second)

    result = repository.list_all()

    assert len(result) == 2
    assert {item.id for item in result} == {
        transaction.id,
        second.id,
    }

    # Изменение полученного списка не должно менять хранилище
    result.clear()
    assert len(repository.list_all()) == 2


def test_replace_transaction(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    repository.add(transaction)

    updated = replace(
        transaction,
        amount=Decimal("2500.00"),
    )

    assert repository.update(updated) is True
    assert repository.get(transaction.id) == updated
    assert transaction.amount == Decimal("1500.50")


def test_replace_nonexistent_transaction(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    assert repository.update(transaction) is False


def test_delete_transaction(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    repository.add(transaction)

    assert repository.delete(transaction.id) is True
    assert repository.get(transaction.id) is None
    assert repository.delete(transaction.id) is False


def test_reject_duplicate_transaction(
    repository: InMemoryTransactionRepository,
    transaction: Transaction,
) -> None:
    repository.add(transaction)

    with pytest.raises(ValueError):
        repository.add(transaction)
