from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import RestrictedError

from finance.models import Account, Category, Transaction, TransactionType
from tests.factories import (
    AccountFactory,
    CategoryFactory,
    TransactionFactory,
    TransferFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def test_amount_is_stored_as_decimal():
    tx = TransactionFactory(amount=Decimal("0.10") + Decimal("0.20"))
    tx.refresh_from_db()

    assert tx.amount == Decimal("0.30")
    assert isinstance(tx.amount, Decimal)


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-100.00")])
def test_amount_must_be_positive(amount):
    with pytest.raises(IntegrityError), transaction.atomic():
        TransactionFactory(amount=amount)


def test_income_and_expense_require_category():
    with pytest.raises(IntegrityError), transaction.atomic():
        TransactionFactory(category=None)


def test_transfer_part_requires_transfer_and_no_category():
    user = UserFactory()
    transfer = TransferFactory(user=user)

    TransactionFactory(
        user=user, type=TransactionType.TRANSFER_OUT, category=None, transfer=transfer
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        TransactionFactory(user=user, type=TransactionType.TRANSFER_IN, transfer=transfer)


def test_regular_transaction_cannot_reference_transfer():
    user = UserFactory()

    with pytest.raises(IntegrityError), transaction.atomic():
        TransactionFactory(user=user, transfer=TransferFactory(user=user))


def test_account_name_is_unique_per_user():
    user = UserFactory()
    AccountFactory(user=user, name="Kaspi Gold")
    AccountFactory(name="Kaspi Gold")

    with pytest.raises(IntegrityError), transaction.atomic():
        AccountFactory(user=user, name="Kaspi Gold")


def test_same_category_name_allowed_for_income_and_expense():
    user = UserFactory()
    CategoryFactory(user=user, name="Other", type="income")
    CategoryFactory(user=user, name="Other", type="expense")

    with pytest.raises(IntegrityError), transaction.atomic():
        CategoryFactory(user=user, name="Other", type="expense")


def test_account_with_transactions_cannot_be_deleted():
    tx = TransactionFactory()

    with pytest.raises(RestrictedError):
        tx.account.delete()


def test_category_with_transactions_cannot_be_deleted():
    tx = TransactionFactory()

    with pytest.raises(RestrictedError):
        tx.category.delete()


def test_deleting_transfer_deletes_its_transactions():
    user = UserFactory()
    transfer = TransferFactory(user=user)
    for tx_type in (TransactionType.TRANSFER_OUT, TransactionType.TRANSFER_IN):
        TransactionFactory(user=user, type=tx_type, category=None, transfer=transfer)

    transfer.delete()

    assert not Transaction.objects.exists()


def test_deleting_user_deletes_all_their_data():
    tx = TransactionFactory()

    tx.user.delete()

    assert not Transaction.objects.exists()
    assert not Account.objects.exists()
    assert not Category.objects.exists()
