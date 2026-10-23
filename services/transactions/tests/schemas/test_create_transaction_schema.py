from decimal import Decimal

import pytest
from pydantic import ValidationError
from transactions.models.transaction import TransactionKind
from transactions.schemas.transaction import TransactionCreate
from transactions.schemas.transaction_patch import TransactionPatch


@pytest.fixture
def valid_payload() -> dict[str, str]:
    return {
        "amount": "1500.50",
        "currency_code": "EUR",
        "kind": "expense",
        "description": "New laptop",
    }


def test_create_valid_transaction(
    valid_payload: dict[str, str],
) -> None:
    transaction = TransactionCreate.model_validate(valid_payload)

    assert transaction.amount == Decimal("1500.50")
    assert isinstance(transaction.amount, Decimal)
    assert transaction.currency_code == 'EUR'
    assert transaction.kind == TransactionKind.EXPENSE
    assert transaction.description == "New laptop"


def test_accepts_maximum_amount(
    valid_payload: dict[str, str],
) -> None:
    payload = {**valid_payload, "amount": "9999999999.99"}

    transaction = TransactionCreate.model_validate(payload)

    assert transaction.amount == Decimal("9999999999.99")


@pytest.mark.parametrize(
    "amount",
    [
        "0",
        "-100",
        "not-a-number",
        "100.123",
        "10000000000.99",
    ],
)
def test_rejects_invalid_amount(
    valid_payload: dict[str, str],
    amount: str,
) -> None:
    payload = {**valid_payload, "amount": amount}

    with pytest.raises(ValidationError):
        TransactionCreate.model_validate(payload)


def test_rejects_invalid_transaction_kind(
    valid_payload: dict[str, str],
) -> None:
    payload = {**valid_payload, "kind": "salary"}

    with pytest.raises(ValidationError):
        TransactionCreate.model_validate(payload)


def test_normalizes_description(
    valid_payload: dict[str, str],
) -> None:
    payload = {
        **valid_payload,
        "description": "  New laptop  ",
    }

    transaction = TransactionCreate.model_validate(payload)

    assert transaction.description == "New laptop"


@pytest.mark.parametrize(
    "description",
    [
        "a" * 201,
        123,
        {}
    ],
)
def test_rejects_invalid_description(
    valid_payload: dict[str, str],
    description: str,
) -> None:
    payload = {**valid_payload, "description": description}

    with pytest.raises(ValidationError):
        TransactionCreate.model_validate(payload)


def test_rejects_extra_fields(
    valid_payload: dict[str, str],
) -> None:
    payload = {**valid_payload, "is_admin": "true"}

    with pytest.raises(ValidationError):
        TransactionCreate.model_validate(payload)


@pytest.mark.parametrize(
    "missing_field",
    ["amount", "currency_code", "kind"],
)
def test_rejects_missing_required_fields(
    valid_payload: dict[str, str],
    missing_field: str,
) -> None:
    payload = valid_payload.copy()
    payload.pop(missing_field)

    with pytest.raises(ValidationError):
        TransactionCreate.model_validate(payload)

def test_description_is_optional() -> None:
    transaction = TransactionCreate.model_validate({
        "amount": "100.00",
        "currency_code": "JPY",
        "kind": "expense",
    })

    assert transaction.description is None


def test_patch_can_clear_description() -> None:
    patch = TransactionPatch.model_validate({
        "description": None,
    })

    assert patch.model_dump(exclude_unset=True) == {
        "description": None,
    }


