import pytest
from django.db import IntegrityError

from tests.factories import BudgetFactory

pytestmark = pytest.mark.django_db


def test_only_one_budget_per_category():
    budget = BudgetFactory()

    with pytest.raises(IntegrityError):
        BudgetFactory(user=budget.user, category=budget.category)
