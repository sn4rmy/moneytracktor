from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from finance.models import Transaction
from tests.factories import AccountFactory, CategoryFactory, TransactionFactory

pytestmark = pytest.mark.django_db

LIST_URL = reverse("transaction-list")


def detail_url(transaction):
    return reverse("transaction-detail", args=[transaction.id])


def result_ids(response):
    return [transaction["id"] for transaction in response.data["results"]]


def valid_data(user, **changes):
    data = {
        "type": "expense",
        "amount": "1500.50",
        "date": "2026-10-01",
        "account": AccountFactory(user=user).id,
        "category": CategoryFactory(user=user, type="expense").id,
        "note": "Lunch",
    }
    data.update(changes)
    return data


def test_create_transaction(auth_client, user):
    account = AccountFactory(user=user, name="Kaspi Gold")
    category = CategoryFactory(user=user, name="Food", type="expense")
    data = {
        "type": "expense",
        "amount": "1500.50",
        "date": "2026-10-01",
        "account": account.id,
        "category": category.id,
        "note": "Lunch",
    }

    response = auth_client.post(LIST_URL, data)

    assert response.status_code == 201
    assert response.data["amount"] == "1500.50"
    assert response.data["account_name"] == "Kaspi Gold"
    assert response.data["category_name"] == "Food"
    transaction = Transaction.objects.get(id=response.data["id"])
    assert transaction.user == user
    assert transaction.amount == Decimal("1500.50")


def test_create_transaction_with_zero_amount_returns_400(auth_client, user):
    response = auth_client.post(LIST_URL, valid_data(user, amount="0"))

    assert response.status_code == 400
    assert "amount" in response.data


def test_create_transaction_without_category_returns_400(auth_client, user):
    data = valid_data(user)
    del data["category"]

    response = auth_client.post(LIST_URL, data)

    assert response.status_code == 400
    assert "category" in response.data


def test_category_type_must_match_transaction_type(auth_client, user):
    income_category = CategoryFactory(user=user, type="income")

    response = auth_client.post(LIST_URL, valid_data(user, category=income_category.id))

    assert response.status_code == 400
    assert "category" in response.data


def test_create_transaction_with_other_users_account_returns_400(auth_client, user):
    response = auth_client.post(LIST_URL, valid_data(user, account=AccountFactory().id))

    assert response.status_code == 400
    assert "account" in response.data
    assert not Transaction.objects.exists()


def test_create_transaction_with_other_users_category_returns_400(auth_client, user):
    response = auth_client.post(LIST_URL, valid_data(user, category=CategoryFactory().id))

    assert response.status_code == 400
    assert "category" in response.data
    assert not Transaction.objects.exists()


def test_list_returns_only_own_transactions(auth_client, user):
    own = TransactionFactory(user=user)
    TransactionFactory()

    response = auth_client.get(LIST_URL)

    assert response.status_code == 200
    assert result_ids(response) == [own.id]


def test_update_transaction(auth_client, user):
    transaction = TransactionFactory(user=user, amount=Decimal("100.00"))

    response = auth_client.patch(detail_url(transaction), {"amount": "250.00"})

    assert response.status_code == 200
    transaction.refresh_from_db()
    assert transaction.amount == Decimal("250.00")


def test_change_type_without_changing_category_returns_400(auth_client, user):
    transaction = TransactionFactory(user=user, type="expense", category__type="expense")

    response = auth_client.patch(detail_url(transaction), {"type": "income"})

    assert response.status_code == 400
    assert "category" in response.data


def test_delete_transaction(auth_client, user):
    transaction = TransactionFactory(user=user)

    response = auth_client.delete(detail_url(transaction))

    assert response.status_code == 204
    assert not Transaction.objects.filter(id=transaction.id).exists()


def test_other_users_transaction_returns_404(auth_client):
    transaction = TransactionFactory(amount=Decimal("100.00"))

    response = auth_client.patch(detail_url(transaction), {"amount": "1.00"})

    assert response.status_code == 404
    transaction.refresh_from_db()
    assert transaction.amount == Decimal("100.00")


def test_transactions_without_token_return_401(api_client):
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


def test_filter_by_date_range(auth_client, user):
    TransactionFactory(user=user, date=date(2026, 9, 30))
    first_day = TransactionFactory(user=user, date=date(2026, 10, 1))
    last_day = TransactionFactory(user=user, date=date(2026, 10, 31))
    TransactionFactory(user=user, date=date(2026, 11, 1))

    response = auth_client.get(LIST_URL, {"date_from": "2026-10-01", "date_to": "2026-10-31"})

    assert result_ids(response) == [last_day.id, first_day.id]


def test_filter_by_account(auth_client, user):
    transaction = TransactionFactory(user=user)
    TransactionFactory(user=user)

    response = auth_client.get(LIST_URL, {"account": transaction.account.id})

    assert result_ids(response) == [transaction.id]


def test_filter_by_category(auth_client, user):
    transaction = TransactionFactory(user=user)
    TransactionFactory(user=user)

    response = auth_client.get(LIST_URL, {"category": transaction.category.id})

    assert result_ids(response) == [transaction.id]


def test_filter_by_type(auth_client, user):
    income = TransactionFactory(user=user, type="income", category__type="income")
    TransactionFactory(user=user, type="expense")

    response = auth_client.get(LIST_URL, {"type": "income"})

    assert result_ids(response) == [income.id]


def test_search_by_note(auth_client, user):
    lunch = TransactionFactory(user=user, note="Lunch with friends")
    TransactionFactory(user=user, note="Taxi")

    response = auth_client.get(LIST_URL, {"search": "lunch"})

    assert result_ids(response) == [lunch.id]


def test_ordering_by_amount(auth_client, user):
    small = TransactionFactory(user=user, amount=Decimal("100.00"))
    big = TransactionFactory(user=user, amount=Decimal("5000.00"))

    response = auth_client.get(LIST_URL, {"ordering": "amount"})

    assert result_ids(response) == [small.id, big.id]


def test_list_is_paginated_by_20(auth_client, user):
    TransactionFactory.create_batch(21, user=user)

    response = auth_client.get(LIST_URL)

    assert response.data["count"] == 21
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None
