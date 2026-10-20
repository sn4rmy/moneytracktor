from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.models import RestrictedError

from finance.models import Account, Category, Transaction, Transfer
from tests.factories import TransactionFactory, TransferFactory

pytestmark = pytest.mark.django_db


def test_amount_is_stored_as_decimal():
    tx = TransactionFactory(amount=Decimal("0.10") + Decimal("0.20"))
    tx.refresh_from_db()

    assert isinstance(tx.amount, Decimal)
    assert tx.amount == Decimal("0.30")


def test_amount_must_be_positive():
    tx = TransactionFactory()
    tx.amount = Decimal("0")

    with pytest.raises(ValidationError) as exc_info:
        tx.full_clean()

    assert "amount" in exc_info.value.message_dict


def test_category_with_transactions_cannot_be_deleted():
    tx = TransactionFactory()

    with pytest.raises(RestrictedError):
        tx.category.delete()


def test_account_with_transactions_cannot_be_deleted():
    tx = TransactionFactory()

    with pytest.raises(RestrictedError):
        tx.account.delete()


def test_deleting_user_deletes_all_their_data():
    tx = TransactionFactory()
    TransferFactory(user=tx.user)

    tx.user.delete()

    assert not Transaction.objects.exists()
    assert not Transfer.objects.exists()
    assert not Account.objects.exists()
    assert not Category.objects.exists()
