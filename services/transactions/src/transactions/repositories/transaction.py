from threading import Lock
from typing import Protocol
from uuid import UUID

from transactions.models.transaction import Transaction


class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> None: ...

    def get(self, transaction_id: UUID) -> Transaction | None: ...

    def list_all(self) -> list[Transaction]: ...

    def update(self, transaction: Transaction) -> bool: ...

    def delete(self, transaction_id: UUID) -> bool: ...


class InMemoryTransactionRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Transaction] = {}
        self._lock = Lock()

    def add(self, transaction: Transaction) -> None:
        with self._lock:
            if transaction.id in self._items:
                raise ValueError("Transaction already exists")

            self._items[transaction.id] = transaction

    def get(self, transaction_id: UUID) -> Transaction | None:
        return self._items.get(transaction_id)

    def list_all(self) -> list[Transaction]:
        return list(self._items.values())

    def update(self, transaction: Transaction) -> bool:
        with self._lock:
            if transaction.id not in self._items:
                return False
            self._items[transaction.id] = transaction
            return True

    def delete(self, transaction_id: UUID) -> bool:
        with self._lock:
            if transaction_id not in self._items:
                return False

            del self._items[transaction_id]
            return True