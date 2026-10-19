import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from budgets.models import BudgetThreshold
from tests.factories import BudgetFactory, BudgetNotificationFactory

pytestmark = pytest.mark.django_db


def test_only_one_budget_per_category():
    budget = BudgetFactory()

    with pytest.raises(IntegrityError), transaction.atomic():
        BudgetFactory(user=budget.user, category=budget.category)


def test_limit_must_be_positive():
    with pytest.raises(IntegrityError), transaction.atomic():
        BudgetFactory(monthly_limit=Decimal("0"))


def test_each_threshold_is_recorded_once_per_month():
    budget = BudgetFactory()
    month = datetime.date(2026, 5, 1)
    BudgetNotificationFactory(budget=budget, month=month, threshold=BudgetThreshold.WARNING)
    BudgetNotificationFactory(budget=budget, month=month, threshold=BudgetThreshold.EXCEEDED)
    BudgetNotificationFactory(
        budget=budget, month=datetime.date(2026, 6, 1), threshold=BudgetThreshold.WARNING
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        BudgetNotificationFactory(budget=budget, month=month, threshold=BudgetThreshold.WARNING)
