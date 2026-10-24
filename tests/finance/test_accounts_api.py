import pytest
from django.urls import reverse

from finance.models import Account
from tests.factories import AccountFactory, TransactionFactory

pytestmark = pytest.mark.django_db


def test_list_returns_only_own_accounts(auth_client, user):
    own = AccountFactory(user=user)
    AccountFactory()

    response = auth_client.get(reverse("account-list"))

    assert response.status_code == 200
    assert [account["id"] for account in response.data] == [own.id]


def test_create_account(auth_client, user):
    response = auth_client.post(reverse("account-list"), {"name": "Kaspi Gold", "type": "card"})

    assert response.status_code == 201
    assert response.data["name"] == "Kaspi Gold"
    assert Account.objects.get(id=response.data["id"]).user == user


def test_create_account_with_unknown_type_returns_400(auth_client):
    response = auth_client.post(reverse("account-list"), {"name": "Wallet", "type": "crypto"})

    assert response.status_code == 400
    assert "type" in response.data


def test_update_account(auth_client, user):
    account = AccountFactory(user=user, name="Old name")

    response = auth_client.patch(reverse("account-detail", args=[account.id]), {"name": "New name"})

    assert response.status_code == 200
    account.refresh_from_db()
    assert account.name == "New name"


def test_delete_account(auth_client, user):
    account = AccountFactory(user=user)

    response = auth_client.delete(reverse("account-detail", args=[account.id]))

    assert response.status_code == 204
    assert not Account.objects.filter(id=account.id).exists()


def test_delete_account_with_transactions_returns_400(auth_client, user):
    transaction = TransactionFactory(user=user)

    response = auth_client.delete(reverse("account-detail", args=[transaction.account.id]))

    assert response.status_code == 400
    assert "detail" in response.data
    assert Account.objects.filter(id=transaction.account.id).exists()


def test_other_users_account_returns_404(auth_client):
    account = AccountFactory()

    response = auth_client.get(reverse("account-detail", args=[account.id]))

    assert response.status_code == 404


def test_accounts_without_token_return_401(api_client):
    response = api_client.get(reverse("account-list"))

    assert response.status_code == 401
