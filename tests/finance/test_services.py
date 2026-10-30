from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.db import IntegrityError

from finance.models import Transaction, TransactionType, Transfer
from finance.services import create_transfer, get_accounts_with_balance
from tests.factories import AccountFactory, TransactionFactory

pytestmark = pytest.mark.django_db


def get_balance(account):
    return get_accounts_with_balance(account.user).get(id=account.id).balance


def test_balance_is_income_minus_expenses(user):
    account = AccountFactory(user=user)
    TransactionFactory(
        user=user,
        account=account,
        type="income",
        category__type="income",
        amount=Decimal("10000.00"),
    )
    TransactionFactory(user=user, account=account, type="expense", amount=Decimal("2500.50"))
    TransactionFactory(user=user, account=account, type="expense", amount=Decimal("1000.00"))

    assert get_balance(account) == Decimal("6499.50")


def test_balance_of_account_without_transactions_is_zero(user):
    account = AccountFactory(user=user)

    assert get_balance(account) == Decimal("0")


def test_create_transfer_creates_expense_and_income(user):
    card = AccountFactory(user=user, name="Card")
    deposit = AccountFactory(user=user, name="Deposit")

    transfer = create_transfer(user, card, deposit, Decimal("5000.00"), date(2026, 10, 1))

    expense = Transaction.objects.get(transfer=transfer, type=TransactionType.EXPENSE)
    income = Transaction.objects.get(transfer=transfer, type=TransactionType.INCOME)
    assert expense.account == card
    assert income.account == deposit
    assert expense.amount == income.amount == Decimal("5000.00")
    assert expense.category is None
    assert income.category is None


def test_transfer_moves_money_between_accounts(user):
    card = AccountFactory(user=user)
    deposit = AccountFactory(user=user)

    create_transfer(user, card, deposit, Decimal("5000.00"), date(2026, 10, 1))

    assert get_balance(card) == Decimal("-5000.00")
    assert get_balance(deposit) == Decimal("5000.00")


def test_create_transfer_is_rolled_back_when_a_transaction_fails(user):
    card = AccountFactory(user=user)
    deposit = AccountFactory(user=user)
    real_create = Transaction.objects.create

    # The expense is saved for real, then the income fails.
    def create_or_fail(**fields):
        if fields["type"] == TransactionType.INCOME:
            raise IntegrityError("Simulated database error")
        return real_create(**fields)

    with patch.object(Transaction.objects, "create", side_effect=create_or_fail):
        with pytest.raises(IntegrityError):
            create_transfer(user, card, deposit, Decimal("5000.00"), date(2026, 10, 1))

    assert not Transfer.objects.exists()
    assert not Transaction.objects.exists()
