from uuid import UUID

from fastapi import APIRouter, status

from transactions.api.dependencies import TransactionServiceDep
from transactions.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
)
from transactions.schemas.transaction_patch import TransactionPatch

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    service: TransactionServiceDep,
) -> TransactionRead:
    transaction = service.create(payload)

    return TransactionRead.model_validate(transaction)

@router.get(
    "",
    response_model=list[TransactionRead],
    status_code=status.HTTP_200_OK,
)
def get_all_transactions(
        service: TransactionServiceDep,
) -> list[TransactionRead]:
    return [TransactionRead.model_validate(transaction) for transaction in service.list_all()]

@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
    status_code=status.HTTP_200_OK,
)
def get_transaction(
        transaction_id: UUID,
        service: TransactionServiceDep
) -> TransactionRead:
    transaction = service.get(transaction_id)

    return TransactionRead.model_validate(transaction)


@router.put("/{transaction_id}", status_code=status.HTTP_200_OK, response_model=TransactionRead)
def replace_transaction(
    transaction_id: UUID, payload: TransactionCreate, service: TransactionServiceDep
) -> TransactionRead:
    return TransactionRead.model_validate(service.replace(transaction_id, payload))

@router.patch(
    "/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=TransactionRead
)
def update_transaction(
        transaction_id: UUID,
        payload: TransactionPatch,
        service: TransactionServiceDep
) -> TransactionRead:
    return TransactionRead.model_validate(service.update(transaction_id, payload))

@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
        transaction_id: UUID,
        service: TransactionServiceDep
) -> None:
    service.delete(transaction_id)

