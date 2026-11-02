from datetime import date
from decimal import Decimal

import pytest

from finance.services import create_transfer
from reports.services import get_expenses_by_category, get_monthly_report, get_summary
from tests.factories import AccountFactory, CategoryFactory, TransactionFactory

pytestmark = pytest.mark.django_db

DATE_FROM = date(2026, 10, 1)
DATE_TO = date(2026, 10, 31)


def add_income(user, amount, day):
    TransactionFactory(user=user, type="income", category__type="income", amount=amount, date=day)


def add_expense(user, amount, day, category=None):
    if category is None:
        category = CategoryFactory(user=user, type="expense")
    TransactionFactory(user=user, type="expense", category=category, amount=amount, date=day)


def test_summary_counts_income_expense_and_total(user):
    add_income(user, Decimal("250000.00"), date(2026, 10, 10))
    add_expense(user, Decimal("2500.50"), date(2026, 10, 12))
    add_expense(user, Decimal("12000.00"), date(2026, 10, 20))

    summary = get_summary(user, DATE_FROM, DATE_TO)

    assert summary == {
        "income": Decimal("250000.00"),
        "expense": Decimal("14500.50"),
        "total": Decimal("235499.50"),
    }


def test_summary_counts_only_transactions_in_period(user):
    add_expense(user, Decimal("100.00"), date(2026, 9, 30))
    add_expense(user, Decimal("200.00"), date(2026, 10, 1))
    add_expense(user, Decimal("300.00"), date(2026, 10, 31))
    add_expense(user, Decimal("400.00"), date(2026, 11, 1))

    summary = get_summary(user, DATE_FROM, DATE_TO)

    assert summary["expense"] == Decimal("500.00")


def test_summary_without_transactions_is_zero(user):
    summary = get_summary(user, DATE_FROM, DATE_TO)

    assert summary == {"income": 0, "expense": 0, "total": 0}


def test_reports_skip_transfers(user):
    card = AccountFactory(user=user)
    deposit = AccountFactory(user=user)
    create_transfer(user, card, deposit, Decimal("50000.00"), date(2026, 10, 15))

    assert get_summary(user, DATE_FROM, DATE_TO) == {"income": 0, "expense": 0, "total": 0}
    assert list(get_expenses_by_category(user, DATE_FROM, DATE_TO)) == []
    assert list(get_monthly_report(user, 2026)) == []


def test_expenses_by_category_sums_each_category(user):
    food = CategoryFactory(user=user, name="Food", type="expense")
    transport = CategoryFactory(user=user, name="Transport", type="expense")
    add_expense(user, Decimal("2000.00"), date(2026, 10, 5), category=food)
    add_expense(user, Decimal("3500.00"), date(2026, 10, 6), category=food)
    add_expense(user, Decimal("4000.00"), date(2026, 10, 7), category=transport)
    add_income(user, Decimal("250000.00"), date(2026, 10, 10))

    report = get_expenses_by_category(user, DATE_FROM, DATE_TO)

    assert list(report) == [
        {"category": food.id, "category__name": "Food", "total": Decimal("5500.00")},
        {"category": transport.id, "category__name": "Transport", "total": Decimal("4000.00")},
    ]


def test_monthly_report_groups_by_month(user):
    add_income(user, Decimal("250000.00"), date(2026, 1, 10))
    add_expense(user, Decimal("1000.00"), date(2026, 1, 15))
    add_expense(user, Decimal("2000.00"), date(2026, 1, 20))
    add_expense(user, Decimal("5000.00"), date(2026, 3, 5))
    add_expense(user, Decimal("9000.00"), date(2025, 12, 31))

    report = get_monthly_report(user, 2026)

    assert list(report) == [
        {"month": 1, "income": Decimal("250000.00"), "expense": Decimal("3000.00")},
        {"month": 3, "income": Decimal("0"), "expense": Decimal("5000.00")},
    ]
