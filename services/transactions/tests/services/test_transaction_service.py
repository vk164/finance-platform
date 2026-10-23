
from decimal import Decimal
from uuid import uuid7

import pytest
from transactions.repositories.transaction import InMemoryTransactionRepository
from transactions.schemas.transaction import TransactionCreate
from transactions.services.transaction import TransactionNotFoundError, TransactionService


@pytest.fixture
def service() -> TransactionService:
    repository = InMemoryTransactionRepository()
    return TransactionService(repository)


@pytest.fixture
def payload() -> TransactionCreate:
    return TransactionCreate(
        amount=Decimal("1500.50"),
        currency_code="EUR",  # type: ignore[arg-type]
        kind="expense",   # type: ignore[arg-type]
        description="New laptop",
    )


def test_create_transaction(
    service: TransactionService,
    payload: TransactionCreate,
) -> None:
    transaction = service.create(payload)

    assert transaction.amount == payload.amount
    assert transaction.created_at == transaction.updated_at
    assert service.get(transaction.id) == transaction


def test_get_nonexistent_transaction(
    service: TransactionService,
) -> None:
    with pytest.raises(TransactionNotFoundError):
        service.get(uuid7())


def test_list_transactions(
    service: TransactionService,
    payload: TransactionCreate,
) -> None:
    service.create(payload)
    service.create(payload)

    assert len(service.list_all()) == 2


def test_delete_transaction(
    service: TransactionService,
    payload: TransactionCreate,
) -> None:
    transaction = service.create(payload)

    service.delete(transaction.id)

    with pytest.raises(TransactionNotFoundError):
        service.get(transaction.id)


def test_delete_nonexistent_transaction(
    service: TransactionService,
) -> None:
    with pytest.raises(TransactionNotFoundError):
        service.delete(uuid7())
