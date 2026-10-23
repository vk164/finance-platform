from typing import Annotated, cast

from fastapi import Depends, Request

from transactions.repositories.transaction import TransactionRepository
from transactions.services.transaction import TransactionService


def get_transaction_service(
    request: Request,
) -> TransactionService:
    repository = cast(
        TransactionRepository,
        request.app.state.transaction_repository,
    )

    return TransactionService(repository)


TransactionServiceDep = Annotated[
    TransactionService,
    Depends(get_transaction_service),
]
