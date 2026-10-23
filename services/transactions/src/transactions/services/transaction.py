from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid7

from transactions.models.transaction import Transaction
from transactions.repositories.transaction import TransactionRepository
from transactions.schemas.transaction import TransactionCreate
from transactions.schemas.transaction_patch import TransactionPatch


class TransactionNotFoundError(Exception):
    pass

class TransactionService:
    def __init__(
        self,
        repository: TransactionRepository,
    ) -> None:
        self._repository = repository

    def create(self, payload: TransactionCreate) -> Transaction:
        now = datetime.now(UTC)

        transaction = Transaction(
            id=uuid7(),
            amount=payload.amount,
            currency_code=payload.currency_code,
            kind=payload.kind,
            description=payload.description,
            created_at=now,
            updated_at=now,
        )

        self._repository.add(transaction)

        return transaction

    def get(self, transaction_id: UUID) -> Transaction:
        tr = self._repository.get(transaction_id)
        if tr is None:
            raise TransactionNotFoundError()
        return tr

    def list_all(self) -> list[Transaction]:
        return self._repository.list_all()

    def delete(self, transaction_id: UUID) -> None:
        self.get(transaction_id)
        self._repository.delete(transaction_id)

    def replace(self, transaction_id: UUID, payload: TransactionCreate):
        tr = self.get(transaction_id)
        changes = payload.model_dump()
        updated = replace(tr, **changes, updated_at=datetime.now(UTC))

        if not self._repository.update(updated):
            raise TransactionNotFoundError()

        return updated

    def update(self, transaction_id: UUID, payload: TransactionPatch):
        tr = self.get(transaction_id)
        changes = payload.model_dump(exclude_unset=True)
        updated = replace(tr, **changes, updated_at=datetime.now(UTC))

        if not self._repository.update(updated):
            raise TransactionNotFoundError()
        
        return updated
