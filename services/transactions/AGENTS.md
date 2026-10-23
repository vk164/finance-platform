# AGENTS.md — Transactions service

Applies under services/transactions/ in addition to the root AGENTS.md. Paths
below are relative to this directory unless prefixed with services/.

## Entry points

Distribution: transactions-srv; Python import package: transactions. Use
transactions.* imports. Check root and service pyproject.toml for Python support
and dependencies; both currently require Python >=3.15.

Under src/transactions/:

- main.py: create_app() owns a fresh repository in
  app.state.transaction_repository and handles TransactionNotFoundError as 404.
  Keep factory-created apps isolated.
- api/dependencies.py: get_transaction_service and TransactionServiceDep connect
  application storage to handlers in api/routers/transactions.py.
- services/transaction.py: TransactionService implements the CRUD use cases.
- repositories/transaction.py: TransactionRepository Protocol and in-memory
  implementation. add rejects duplicates with ValueError; get returns None when
  absent; update/delete return bool indicating whether a record existed.
- models/transaction.py: frozen, slotted Transaction and TransactionKind StrEnum.
- schemas/transaction.py and schemas/transaction_patch.py: external contracts.

The working CRUD chain is synchronous and in-memory. Individual repository writes
are locked; service read/modify/write operations are not atomic. List ordering
has no explicit public contract. Recheck these details before persistence changes.

## Transaction contract

- IDs are service-generated UUIDv7. created_at and updated_at are aware UTC
  datetimes; updates retain id and created_at and set updated_at on the server.
- amount is positive Decimal, at most 12 total digits and two decimal places.
  Preserve string serialization of amounts in JSON responses.
- currency_code matches ^[A-Z]{3}$, including BTC. No whitelist or case conversion.
- kind preserves the wire values income, expense, and transfer.
- description is optional/nullable, strips surrounding whitespace, has a maximum
  of 200 characters and no minimum length.
- Create and PATCH reject extra fields. PUT uses TransactionCreate: amount,
  currency_code, and kind are required; omitted description becomes None.
- PATCH uses model_dump(exclude_unset=True), rejects an empty body object and
  null for required domain fields, and permits description=null to clear it.
- Collection route: /transactions. POST returns 201; GET/list/PUT/PATCH return
  200; DELETE returns 204 without a body. Missing records return 404; invalid
  UUIDs or bodies return 422. Preserve response schemas and error detail behavior.

## Running and testing

Run from the repository root:

```sh
uv run --package transactions-srv uvicorn transactions.main:create_app --factory --reload --reload-dir services/transactions/src
uv run --package transactions-srv pytest services/transactions/tests -v
```

Tests mirror layers in tests/{models,schemas,repositories,services,api}. API tests
use TestClient(create_app()) and must remain independent of PostgreSQL. Follow
root verification rules; start with the affected test module. For update changes,
cover omission vs null, preserved fields, persistence, and non-mutation on error.
Include arbitrary valid currency codes and relevant enum values in regressions.

A service-local uv.lock also exists. Use the root workspace workflow rather than
regenerating the service lockfile as incidental cleanup.

## Persistence specifics

SQLAlchemy asyncio and asyncpg dependencies do not mean persistence is implemented.
At this writing, db/models/transaction.py is a placeholder and no database
repository, session dependency, or Alembic migration setup exists. Reinspect these
paths when starting database work and update this guidance as implementation grows.

Map money to NUMERIC(12, 2), UUIDs to UUID columns, timestamps with timezone support,
and description to a nullable column. Follow root lifecycle and migration rules.

db/check.py is a standalone connectivity check using DATABASE_URL; it runs a
read-only timestamp query and disposes its engine. It is not application startup
or migration management. Inspect the root docker-compose.yaml for local PostgreSQL
settings instead of copying connection details into instructions or source.
