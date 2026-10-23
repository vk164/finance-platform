from collections.abc import Iterator
from datetime import datetime
from typing import Any
from uuid import uuid7

import pytest
from fastapi.testclient import TestClient
from transactions.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def transaction_payload() -> dict[str, str]:
    return {
        "amount": "1500.50",
        "currency_code": "EUR",
        "kind": "expense",
        "description": "New laptop",
    }


def test_create_and_get_transaction(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    response = client.post(
        "/transactions",
        json=transaction_payload,
    )

    assert response.status_code == 201

    transaction = response.json()

    assert transaction["amount"] == "1500.50"

    transaction_id = transaction["id"]

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id


def test_delete_transaction(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    created = client.post(
        "/transactions",
        json=transaction_payload,
    ).json()

    transaction_id = created["id"]

    response = client.delete(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 204
    assert response.content == b""

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 404

def create_transaction(
    client: TestClient,
    payload: dict[str, str],
) -> dict[str, Any]:
    response = client.post("/transactions", json=payload)

    assert response.status_code == 201

    return response.json()


def test_put_replaces_transaction(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    created = create_transaction(client, transaction_payload)

    replacement = {
        "amount": "2500.00",
        "currency_code": "USD",
        "kind": "income",
        "description": "Updated transaction",
    }

    response = client.put(
        f"/transactions/{created['id']}",
        json=replacement,
    )

    assert response.status_code == 200

    updated = response.json()

    # Все редактируемые поля заменены
    for key, value in replacement.items():
        assert updated[key] == value

    # Системные поля сохраняются
    assert updated["id"] == created["id"]
    assert updated["created_at"] == created["created_at"]

    # Время изменения не раньше времени создания
    assert datetime.fromisoformat(
        updated["updated_at"]
    ) >= datetime.fromisoformat(created["updated_at"])

    # Данные действительно сохранились
    stored = client.get(f"/transactions/{created['id']}")

    assert stored.status_code == 200
    assert stored.json() == updated


def test_put_requires_all_fields(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    created = create_transaction(client, transaction_payload)

    response = client.put(
        f"/transactions/{created['id']}",
        json={"description": "Only description"},
    )

    assert response.status_code == 422


def test_patch_updates_only_provided_fields(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    created = create_transaction(client, transaction_payload)

    response = client.patch(
        f"/transactions/{created['id']}",
        json={"description": "Updated description"},
    )

    assert response.status_code == 200

    updated = response.json()

    # Изменилось только описание
    assert updated["description"] == "Updated description"

    # Остальные бизнес-поля остались прежними
    assert updated["amount"] == created["amount"]
    assert updated["currency_code"] == created["currency_code"]
    assert updated["kind"] == created["kind"]

    # Системные поля
    assert updated["id"] == created["id"]
    assert updated["created_at"] == created["created_at"]

    stored = client.get(f"/transactions/{created['id']}")

    assert stored.json() == updated


def test_patch_updates_multiple_fields(
    client: TestClient,
    transaction_payload: dict[str, str],
) -> None:
    created = create_transaction(client, transaction_payload)

    response = client.patch(
        f"/transactions/{created['id']}",
        json={
            "amount": "999.99",
            "currency_code": "RUB",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["amount"] == "999.99"
    assert updated["currency_code"] == "RUB"

    assert updated["kind"] == created["kind"]
    assert updated["description"] == created["description"]


@pytest.mark.parametrize(
    "invalid_patch",
    [
        {},
        {"amount": None},
        {"amount": "-100"},
        {"amount": "100.123"},
        {"description": "a"*205},
        {"unknown_field": "value"},
    ],
)
def test_patch_rejects_invalid_payload(
    client: TestClient,
    transaction_payload: dict[str, str],
    invalid_patch: dict[str, Any],
) -> None:
    created = create_transaction(client, transaction_payload)

    response = client.patch(
        f"/transactions/{created['id']}",
        json=invalid_patch,
    )

    assert response.status_code == 422

    # Ошибочный запрос не должен менять данные
    stored = client.get(f"/transactions/{created['id']}")

    assert stored.status_code == 200
    assert stored.json() == created


@pytest.mark.parametrize("method", ["PUT", "PATCH"])
def test_update_nonexistent_transaction(
    client: TestClient,
    transaction_payload: dict[str, str],
    method: str,
) -> None:
    transaction_id = uuid7()

    payload = (
        transaction_payload
        if method == "PUT"
        else {"description": "Updated"}
    )

    response = client.request(
        method,
        f"/transactions/{transaction_id}",
        json=payload,
    )

    assert response.status_code == 404


@pytest.mark.parametrize("method", ["PUT", "PATCH"])
def test_update_rejects_invalid_uuid(
    client: TestClient,
    transaction_payload: dict[str, str],
    method: str,
) -> None:
    response = client.request(
        method,
        "/transactions/invalid-uuid",
        json=transaction_payload,
    )

    assert response.status_code == 422