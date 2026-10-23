from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from transactions.api.routers.transactions import router as transactions_router
from transactions.repositories.transaction import InMemoryTransactionRepository
from transactions.services.transaction import TransactionNotFoundError


def create_app() -> FastAPI:
    app = FastAPI(
        title="Transaction Service",
        version="0.1.0",
    )

    app.state.transaction_repository = (
        InMemoryTransactionRepository()
    )

    app.include_router(transactions_router)

    @app.exception_handler(TransactionNotFoundError)
    async def handle_not_found(
        request: Request,
        exc: TransactionNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
