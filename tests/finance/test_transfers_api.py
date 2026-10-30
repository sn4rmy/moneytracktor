import pytest
from django.urls import reverse

from finance.models import Transaction, Transfer
from tests.factories import AccountFactory

pytestmark = pytest.mark.django_db

URL = reverse("transfer-create")


def valid_data(user, **changes):
    data = {
        "from_account": AccountFactory(user=user).id,
        "to_account": AccountFactory(user=user).id,
        "amount": "5000.00",
        "date": "2026-10-01",
    }
    data.update(changes)
    return data


def test_create_transfer(auth_client, user):
    card = AccountFactory(user=user)
    deposit = AccountFactory(user=user)
    data = {
        "from_account": card.id,
        "to_account": deposit.id,
        "amount": "5000.00",
        "date": "2026-10-01",
    }

    response = auth_client.post(URL, data)

    assert response.status_code == 201
    assert response.data["amount"] == "5000.00"
    transfer = Transfer.objects.get(id=response.data["id"])
    assert transfer.user == user
    assert transfer.transactions.count() == 2

    card_response = auth_client.get(reverse("account-detail", args=[card.id]))
    assert card_response.data["balance"] == "-5000.00"


def test_transfer_to_same_account_returns_400(auth_client, user):
    account = AccountFactory(user=user)

    response = auth_client.post(
        URL, valid_data(user, from_account=account.id, to_account=account.id)
    )

    assert response.status_code == 400
    assert "to_account" in response.data
    assert not Transfer.objects.exists()


@pytest.mark.parametrize("field", ["from_account", "to_account"])
def test_transfer_with_other_users_account_returns_400(auth_client, user, field):
    data = valid_data(user)
    data[field] = AccountFactory().id

    response = auth_client.post(URL, data)

    assert response.status_code == 400
    assert field in response.data
    assert not Transaction.objects.exists()


def test_transfer_with_zero_amount_returns_400(auth_client, user):
    response = auth_client.post(URL, valid_data(user, amount="0"))

    assert response.status_code == 400
    assert "amount" in response.data


def test_transfer_without_token_returns_401(api_client):
    response = api_client.post(URL, {})

    assert response.status_code == 401
